from __future__ import print_function, division
from builtins import range
import gym
import os
import sys
import pandas as pd
from gym import wrappers
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import turtle
import RedTieBot

def build_state(features):
    return int("".join(map(lambda feature: str(int(feature)), features)))

def to_bin(value, bins):
    return np.digitize(x=[value], bins=bins)[0]

class FeatureTransformer:
    def __init__(self):
        '''
        self.bot_xposition_bins = np.linspace(0, 821, 82)
        self.bot_yposition_bins = np.linspace(0, 1598, 160)
        self.bot_facing_bins = np.linspace(0,2*np.pi,24)
        self.bot_lspeed_bins = np.linspace(-128,127,256)
        self.bot_rspeed_bins = np.linspace(-128,127,256)
        '''
    def transform(self, observation):
        x, y, facing, l_speed, r_speed = observation.values()
        '''
        return build_state([
            to_bin(x, self.bot_xposition_bins),
            to_bin(y, self.bot_yposition_bins),
            to_bin(facing, self.bot_facing_bins),
            to_bin(l_speed, self.bot_lspeed_bins),
            to_bin(r_speed, self.bot_rspeed_bins),
        ])
        '''
        return x*24*160+y*24+facing
class Model:
    def __init__(self, env, feature_transformer):
        self.env = env
        self.feature_transformer = feature_transformer

        self.num_states = 82*160*24#10**env.observation_space.shape[0]
        ############
        self.num_actions = 9
        self.load()
        self.counter = 0

    def reset(self):
        self.counter = 0
        self.target = None

    def get_target(self):
        if self.target is None:
            self.target = self.env.get_a_target
        return self.target

    def save(self):
        np.save('save_Q.npy', self.Q)

    def load(self):
        if os.path.exists('save_Q.npy'):
            self.Q = np.load('save_Q.npy')
        else:
            self.Q = np.random.uniform(low=-1, high=1, size=(self.num_states, self.num_actions))
            
    def predict(self, s):
        x=self.feature_transformer.transform(s)
        return self.Q[x]

    def update(self,s,a,G):
        x=self.feature_transformer.transform(s)
        self.Q[x,a] += 10e-3*(G-self.Q[x,a])

    def sample_action(self,s,eps):
        self.counter += 1
        #if self.counter < 2000:
            #return self.calculated_path(s)
        if np.random.random() < eps:
            #print('random')
            return self.env.action_space.sample()
        else:
            p=self.predict(s)
            #print('prob: {}'.format(p))
            return self.env.action_space.fromQ(np.argmax(p))
'''
    def calculated_path(self, observation):
        x, y, facing = get_target()
        if self.checkspot(x,y):
            self.turn(angle=facing):
            
    def checkspot(self,x,y):
        a=self.env.reward_point()
        for n in range(len(a)):
            if x in a[n][0] and y in a[n][1]:
                return True
        return False

    def turn(self, x=None, y=None, angle=None):
        if angle != None:
            
'''
def play_one(model,eps,gamma):
    observation=env.reset()
    model.reset()
    done=False
    totalreward=0
    iters=0
    path = []
    while not done and iters<100000:
        action=model.sample_action(observation, eps)
        prev_observation=observation
        observation, reward, done, info = env.step(action)
        path.append((observation, reward, action))
        totalreward+= reward
        #if done and iters<299==0:
        #    reward=-300

        G=reward+gamma*np.max(model.predict(observation))
        model.update(prev_observation, action, G)
        iters+=1

    #if totalreward > 0:
        #print(path)
    return totalreward

def plot_running_avg(totalrewards):
    N=len(totalrewards)
    running_avg=np.empty(N)
    for t in range(N):
        running_avg[t]=totalrewards[max(0,t-100):(t+1)].mean()
    plt.plot(running_avg)
    plt.title('Rewards')
    plt.show()
    print(totalrewards)
    nameeverything = raw_input("save file? ")
    if nameeverything == "yes":
        model.save()

if __name__ == '__main__':
    env = gym.make('redtiebot-v0')
    ft = FeatureTransformer()
    model = Model(env,ft)
    gamma = 0.9

    if 'monitor' in sys.argv:
        filename = os.path.basename(__file__).split('.')[0]
        monitor_dir = './' + filename + '_' + str(datetime.now())
        env = wrappers.Monitor(env, monitor_dir)

    N=10000
    totalrewards=np.empty(N)
    import pdb; pdb.set_trace()
    print(10000)
    for n in range(10000):
        print(n)
        eps=1.0/np.sqrt(n+1)
        totalreward=play_one(model, eps, gamma)
        totalrewards[n] = totalreward
        if n%100==0:
            print("avg reward for last 100 episodes:", totalrewards[-100:].mean())
            print("total rewards:", totalrewards.sum())
    #plt.plot(totalrewards)
    #plt.title("Rewards")
    #plt.show()
    plot_running_avg(totalrewards)
    print('Total rewards are' + totalreward + '!')
