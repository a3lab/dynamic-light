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
#    print("Received data {} {} {}".format(unused_addr, args, values))
    if not env._observation_flag:
        # Record values.
        env._current_observation = values
        # Reset flag.
        env._observation_flag = True

class OscEnv(Env):
    _observation_flag = False
    _current_observation = None
    reward_function = None

    def __init__(self, action_space, observation_space, reward_function, observationAddress="/env/observation", actionAddress="/env/action", observationPort=8000, actionPort=8001, actionIP="127.0.0.1"):
        self.action_space = action_space
        self.observation_space = observation_space
        self.reward_function = reward_function

        self.observationAddress = observationAddress
        self.actionAddress = actionAddress

        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map(observationAddress, _receive_observation, self)

        self.server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 8000), self.dispatcher)
        self.client = udp_client.SimpleUDPClient(actionIP, actionPort)
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.start()

    # Get observation (blocking).
    def _get_observation(self):
        self._observation_flag = False
        # Waiting for observation to arrive.
        while not self._observation_flag:
            time.sleep(0.01)
        return self._current_observation

    def step(self, action):
#        print("Step: {}".format(action))
        # Take action.
        self.client.send_message(self.actionAddress, int(action))

        # Wait to receive OSC message.
        observation = self._get_observation()

        # Collect observation.
        observation = self._current_observation
        reward = self.reward_function(observation)
        return observation, reward, False, {}

    def reset(self):
        return self._get_observation()

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
        raise NotImplementedError()
