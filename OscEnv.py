from rl.core import Env
import time
import threading

from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client

def _receive_observation(unused_addr, args, *values):
    # The OscEnv object.
    env = args[0]
    print("Received data {} {} {}".format(unused_addr, args, values))
    if not env._observation_flag:
        # Record values.
        env._current_reward = values[0]
        env._current_observation = values[1:]
        print("{} {}".format(env._current_reward, env._current_observation))
        # Reset flag.
        env._observation_flag = True

class OscEnv(Env):
    _observation_flag = False
    _current_observation = None
    _current_reward = None
    reward_function = None

    def __init__(self, action_space, observation_space, observation_address="/env/observation", action_address="/env/action", observation_port=8000, action_port=8001, action_ip="127.0.0.1"):
        self.action_space = action_space
        self.observation_space = observation_space
        self.observation_address = observation_address
        self.action_address = action_address

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/", print)
        self.dispatcher.map(observation_address, _receive_observation, self)

        self.server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", observation_port), self.dispatcher)
        self.client = udp_client.SimpleUDPClient(action_ip, action_port)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()

        print("OSCEnv client/action={}:{} server/observation=localhost:{}".format(action_ip, action_port, observation_port))

    # Get observation (blocking).
    def _get_observation(self):
        self._observation_flag = False
        print("waiting to get obs")
        # Waiting for observation to arrive.
        while not self._observation_flag:
            time.sleep(0.01)
        return self._current_observation, self._current_reward

    def step(self, action):
        print("Step: {}".format(action))
        # Take action.
        self.client.send_message(self.action_address, int(action))

        # Wait to receive OSC message.
        observation, reward = self._get_observation()
        return observation, reward, False, {}

    def reset(self):
        print("Reset")
        observation, _ = self._get_observation()
        return observation

    def render(self, mode='human', close=False):
        raise NotImplementedError()

    def close(self):
        self.server.shutdown()
        return

    def seed(self, seed=None):
        """Sets the seed for this env's random number generator(s).
        # Returns
            Returns the list of seeds used in this env's random number generators
        """
        return # for now do nothing
        # raise NotImplementedError()

    def configure(self, *args, **kwargs):
        """Provides runtime configuration to the environment.
        This configuration should consist of data that tells your
        environment how to run (such as an address of a remote server,
        or path to your ImageNet data). It should not affect the
        semantics of the environment.
        """
        return
