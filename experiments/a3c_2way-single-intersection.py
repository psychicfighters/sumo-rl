import argparse
import os
import sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Please declare the environment variable 'SUMO_HOME'")
import pandas as pd
import ray
from ray.rllib.agents.a3c.a3c import A3CTrainer
from ray.rllib.agents.a3c.a3c_tf_policy import A3CTFPolicy
from ray.tune.registry import register_env
from ray.tune.logger import pretty_print
from gym import spaces
import numpy as np
from sumo_rl.environment.env import SumoEnvironment
import traci

def policy_mapping(id):
    return '0'

if __name__ == '__main__':
    ray.init()

    register_env("2way-single-intersection", lambda _: SumoEnvironment(net_file='nets/2way-single-intersection/single-intersection.net.xml',
                                                    route_file='nets/2way-single-intersection/single-intersection-gen.rou.xml',
                                                    out_csv_name='outputs/2way-single-intersection/a3c-contexts',
                                                    use_gui=False,
                                                    num_seconds=100000,
                                                    time_to_load_vehicles=120,
                                                    max_depart_delay=0,
                                                    phases=[
                                                        traci.trafficlight.Phase(32, "GGrrrrGGrrrr"),  
                                                        traci.trafficlight.Phase(2, "yyrrrryyrrrr"),
                                                        traci.trafficlight.Phase(32, "rrGrrrrrGrrr"),   
                                                        traci.trafficlight.Phase(2, "rryrrrrryrrr"),
                                                        traci.trafficlight.Phase(32, "rrrGGrrrrGGr"),   
                                                        traci.trafficlight.Phase(2, "rrryyrrrryyr"),
                                                        traci.trafficlight.Phase(32, "rrrrrGrrrrrG"), 
                                                        traci.trafficlight.Phase(2, "rrrrryrrrrry")
                                                        ]))

    trainer = A3CTrainer(env="2way-single-intersection", config={
        "multiagent": {
            "policy_graphs": {
                '0': (A3CTFPolicy, spaces.Box(low=np.zeros(21), high=np.ones(21)), spaces.Discrete(4), {})
            },
            "policy_mapping_fn": policy_mapping  # Traffic lights are always controlled by this policy
        },
        "lr": 0.0001,
    })
    
    while True:
        result = trainer.train()
        print(pretty_print(result))