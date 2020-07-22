import numpy as np
import random

def activation(x, derivative = False, function = 'sigmoid'):
    
    if derivative:
        if function == 'sigmoid':
            return activation(x) * (1 - activation(x))
        else:
            pass
    else:
        if function == 'sigmoid':
            return 1/(1+np.exp(-x))
        else:
            pass

def costfunction(true, pred):

    cost = 1/2 * ((true - pred)**2)
    return cost


def derivcostfunction(true, pred, size):
     return true - pred
     

class NeuralNetwork():
    
    def __init__ (self, size, seed = 69):
        self.seed = seed
        np.random.seed(self.seed)
        
        self.size = size
        self.weights = [np.random.random((self.size[i], self.size[i-1]))*2 -1 for i in range(1, len(self.size))]
        self.bias = [np.random.random((n,1))*2 -1 for n in self.size[1:]]
        
    def forward(self, inp):
        a = inp
        pre_activations = []
        activations = [a]
        for w, b in zip(self.weights, self.bias):
            z = np.dot(w, a) + b
            a  = activation(z)
            pre_activations.append(z)
            activations.append(a)
            
        
        return a, activations, pre_activations
    
    def calcDeltas(self, activations, pre_activations, a, target):
        deltal = derivcostfunction(target, a, self.size) * activation(pre_activations[-1], derivative = True)
        deltas =  [0] * (len(self.size) -1)
        deltas[-1] = deltal
        
        err = derivcostfunction(target, a, self.size)
 
        
        for i in range(len(deltas) -2 ,-1, -1):
            err = np.dot(self.weights[i+1].transpose(),err)
            
            delta =  err * activation(pre_activations[i+1], derivative = True)
            
            deltas[i] = delta
    
        return deltas
    def backprop(self, activations, pre_activations, a, learnRate, deltas):
        dW = []
        dB = []
        deltas = deltas

        for i in range(len(self.size) -1 ):
            
            dw1 = np.dot(deltas[i], pre_activations[i].transpose())
            db1 = deltas[i]
            dW.append(dw1)

            dB.append(db1)

        return dW, dB
    
    def adjustWeights(self, dW, dB, lr):
        
        
        for i in range(len(self.size)-1):
            
            self.weights[i] = self.weights[i]+lr*dW[i]
            self.bias[i] = np.add(self.bias[i], lr * dB[i])            
            
            
    def train(self, data, labels, iterations, lr):

        for i in range(iterations):
            ri = np.random.randint(len(data))
            testpoint = data[ri]
            testlabels = np.zeros((self.size[-1], 1))
            y = labels[ri]
            testlabels[y] = 1
            
            a = NeuralNetwork.forward(self, testpoint)
            b = NeuralNetwork.calcDeltas(self, a[2],a[1], a[0], testlabels)
            c = NeuralNetwork.backprop(self, a[2], a[1], a[0], lr, b)
            d = NeuralNetwork.adjustWeights(self, c[0], c[1], lr)
            
    def predict(self, input1):
        a = NeuralNetwork.forward(self, input1)
        x = 0
        i = None
        for i in range(len(a[0])):
            if x<a[0][i]:
                x = a[0][i]
                d = i
        return d

        
    
    #More functions for neuro-evo
    
    def copy(self):
        size = self.size
        seed = self.seed
        nCopy = NeuralNetwork(size, seed = seed)
        
        return nCopy
    
    def mutate(self, rate):
        def _mutate(val):
            seed = self.seed
            self.seed = None
            np.random.seed(self.seed)
            
            if np.random.random() < rate:
                val = np.random.random() * 4 -2
                self.seed = seed
                return val
            else:
                self.seed = seed
                return 0
        
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                a = self.weights[i][j]
                self.weights[i][j] += list(map(_mutate, a))
        for i in range(len(self.bias)):
            for j in range(len(self.bias[i])):
                a = self.bias[i][j]
                self.bias[i][j] += list(map(_mutate, a))
            
    def crossover(self, net1, net2):
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                for k in range(len(self.weights[i][j])):
                    rnet = random.choice([net1.weights, net2.weights])
                    rchoice = rnet[i][j][k]
                    self.weights[i][j][k] = rchoice
        for i in range(len(self.bias)):
            for j in range(len(self.bias[i])):
                for k in range(len(self.bias[i][j])):
                    rnet = random.choice([net1.bias, net2.bias])
                    rchoice = rnet[i][j][k]
                    self.bias[i][j][k] = rchoice
        
        
c = NeuralNetwork([1,4,1])
d = NeuralNetwork([1,4,1], seed = 420)
e = NeuralNetwork([1,4,1], seed = None)      

e.crossover(c, d)
print(e.bias)
#print()
#print(c.weights)
#print()
#print(d.weights)  
e.mutate(1)
print(e.bias)

