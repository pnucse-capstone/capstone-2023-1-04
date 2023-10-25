import time
import random

import torch
import torch.nn as nn
import torch.optim as optim

from utils import epoch_time
from model.optim import ScheduledAdam
from model.transformer import Transformer

from tqdm import tqdm
from make_vocab import tokenizer_kor
import pickle
from hangul_utils import join_jamos

random.seed(32)
torch.manual_seed(32)
torch.backends.cudnn.deterministic = True


class Trainer:
    def __init__(self, params, mode, train_iter=None, valid_iter=None, test_iter=None, patience=10):
        self.params = params
        self.patience = patience
        self.patience_counter = 0

        # Train mode
        if mode == 'train':
            self.train_iter = train_iter
            self.valid_iter = valid_iter

        # Test mode
        else:
            self.test_iter = test_iter

        self.model = Transformer(self.params)
        self.model.to(self.params.device)

        # Scheduling Optimzer
        self.optimizer = ScheduledAdam(
            optim.Adam(self.model.parameters(), betas=(0.9, 0.98), eps=1e-9),
            hidden_dim=params.hidden_dim,
            warm_steps=params.warm_steps
        )

        self.criterion = nn.CrossEntropyLoss()
        self.criterion.to(self.params.device)

        pickle_kor = open('pickles/kor.pickle', 'rb')
        self.kor = pickle.load(pickle_kor)

        pickle_eng = open('pickles/eng.pickle', 'rb')
        self.eng = pickle.load(pickle_eng)

    def train(self):
        print(self.model)
        print(f'The model has {self.model.count_params():,} trainable parameters')
        best_valid_loss = float('inf')

        for epoch in range(self.params.num_epoch):
            self.model.train()
            epoch_loss = 0
            start_time = time.time()
            t = tqdm(self.train_iter, desc=f'Epoch {epoch + 1}')

            for batch in t:
                # For each batch, first zero the gradients
                self.optimizer.zero_grad()
                target = batch.kor
                source = batch.eng

                # target sentence consists of <sos> and following tokens (except the <eos> token)
                output = self.model(source, target[:, :-1])[0]

                # ground truth sentence consists of tokens and <eos> token (except the <sos> token)
                output = output.contiguous().view(-1, output.shape[-1])
                target = target[:, 1:].contiguous().view(-1)
                # output = [(batch size * target length - 1), output dim]
                # target = [(batch size * target length - 1)]
                loss = self.criterion(output, target)
                loss.backward()

                # clip the gradients to prevent the model from exploding gradient
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.params.clip)

                self.optimizer.step()

                # 'item' method is used to extract a scalar from a tensor which only contains a single value.
                epoch_loss += loss.item()

                t.set_postfix({'loss': loss.item()})

            train_loss = epoch_loss / len(self.train_iter)
            valid_loss, val_acc = self.evaluate()

            end_time = time.time()
            epoch_mins, epoch_secs = epoch_time(start_time, end_time)

            if valid_loss < best_valid_loss:
                best_valid_loss = valid_loss
                torch.save(self.model.state_dict(), self.params.save_model)
                self.patience_counter = 0

            else:
                self.patience_counter += 1
                print("Patience: ", self.patience_counter)
                if self.patience_counter >= self.patience:
                    print("Early stopping")
                    return

            print(f'Epoch: {epoch+1:02} | Epoch Time: {epoch_mins}m {epoch_secs}s')
            print(f'\tTrain Loss: {train_loss:.3f} | Val. Loss: {valid_loss:.3f} | Val acc: {val_acc:.3f}')

    def evaluate(self):
        self.model.eval()
        epoch_loss = 0
        total_correct = 0
        total_count = 0

        with torch.no_grad():
            t = tqdm(self.valid_iter, desc='Validating')
            for batch in t:
                target = batch.kor
                source = batch.eng

                output = self.model(source, target[:, :-1])[0]
                output_dim = output.shape[-1]
                output = output.contiguous().view(-1, output_dim)

                target = target[:, 1:].contiguous()

                loss = self.criterion(output, target.view(-1))

                epoch_loss += loss.item()

                predicted = output.argmax(dim=1).view(target.shape[0], -1)  # 원래 시퀀스 shape로 변경
                for i in range(target.shape[0]):
                    total_count += 1
                    target_i = target[i, :]
                    predicted_i = predicted[i, :]

                    target_token = [self.kor.vocab.itos[token] for token in target_i]
                    try:
                        target_translation = ''.join(target_token[:target_token.index('<eos>')])
                    except:
                        target_translation = ''.join(target_token[:])

                    pred_token = [self.kor.vocab.itos[token] for token in predicted_i]
                    try:
                        pred_translation = ''.join(pred_token[:pred_token.index('<eos>')])
                    except:
                        pred_translation = ''.join(pred_token[:])

                    if pred_translation.replace("<pad>", "") == target_translation:
                        total_correct += 1

                t.set_postfix({'loss': loss.item(), 'corr': total_correct, 'total': total_count, 'acc':total_correct/total_count})

        avg_acc = total_correct / total_count * 100

        return epoch_loss / len(self.valid_iter), avg_acc

    def inference(self):
        self.model.load_state_dict(torch.load(self.params.save_model))
        self.model.eval()
        epoch_loss = 0
        total_correct = 0
        total_count = 0
        with torch.no_grad():
            for batch in self.test_iter:
                target = batch.kor
                source = batch.eng

                output = self.model(source, target[:, :-1])[0]

                output = output.contiguous().view(-1, output.shape[-1])

                predicted = output.argmax(1)

                target = target[:, 1:].contiguous()
                loss = self.criterion(output, target.view(-1))

                epoch_loss += loss.item()

                predicted = output.argmax(dim=1).view(target.shape[0], -1)

                for i in range(target.shape[0]):
                    total_count += 1
                    source_i = source[i, :]
                    target_i = target[i, :]
                    predicted_i = predicted[i, :]

                    source_token = [self.eng.vocab.itos[token] for token in source_i]
                    try:
                        source_translation = ''.join(source_token[:source_token.index('<pad>')])
                    except:
                        source_translation = ''.join(source_token[:])
                    target_token = [self.kor.vocab.itos[token] for token in target_i]
                    try:
                        target_translation = ''.join(target_token[:target_token.index('<eos>')])
                    except:
                        target_translation = ''.join(target_token[:])

                    pred_token = [self.kor.vocab.itos[token] for token in predicted_i]
                    try:
                        pred_translation = ''.join(pred_token[:pred_token.index('<eos>')])
                    except:
                        pred_translation = ''.join(pred_token[:])

                    if pred_translation == target_translation:
                        total_correct += 1
                #
                #     print(
                #         f"Source: {source_translation}, Predicted: {join_jamos(pred_translation)}, Target: {join_jamos(target_translation)}")
                #

        print(total_correct, total_count)
        test_loss = epoch_loss / len(self.test_iter)
        avg_acc = total_correct / total_count * 100
        print(f'Test Loss: {test_loss:.3f}, acc: {avg_acc}')
