"""
This module defines the BaseFSM class which implements a basic Finite State Machine (FSM) framework. 
The FSM can transition between states defined as methods within a subclass, allowing for flexible 
and dynamic state management.

Classes:
    - BaseFSM: A base class for implementing a Finite State Machine (FSM).

Usage:
    To create a custom FSM, subclass BaseFSM and define methods corresponding to each state. The FSM 
    will transition between these states based on the logic defined in the `fsm` method.
"""

from core.utils import Utils
from enum import Enum, auto
from typing import Type

class BaseState(Enum):
    """
    BaseState defines the fundamental states for the FSM.
    Additional specific states should be added in child classes.

    Attributes:
        INITIAL: The initial state of the FSM.
        END: The end state of the FSM.
    """
    INITIAL = auto()
    END = auto()

class BaseFSM:
    """
    BaseFSM is a foundational class for creating Finite State Machines (FSM).

    This class provides the core logic for state transitions and state handling. To use this class, 
    subclass it and define methods that correspond to each state. The FSM will transition between 
    these states based on the logic provided in the `fsm` method.

    Attributes:
        logger (logging.Logger): The logger instance for the FSM.
        States (BaseState): A class containing the possible states for the FSM.
        current_state (str): The current state of the FSM.

    Methods:
        __init__(self, **kwargs): Initializes the FSM with configuration options.
        _initialize(self): Additional initialization steps to be implemented by subclasses.
        run(self): Runs the FSM, transitioning through states until reaching the END state.
        fsm(self) -> Type[BaseState]: Defines the FSM logic and transitions to the next state.
    """
    def __init__(self, **kwargs):
        """
        Initialize the BaseFSM with configuration options.

        Args:
            **kwargs: Arbitrary keyword arguments representing configuration options.
        """
        self.logger = Utils.get_logger()
        self.States = BaseState
        self.current_state = BaseState.INITIAL

        # Load configuration from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)
        # Additional initialization if needed
        self._initialize()

    def _initialize(self):
        """
        Additional initialization steps can be implemented by subclasses.
        """
        self.logger.debug("BaseFSM initialization complete.")

    def run(self, continuous=True):
        """
        Run the FSM, transitioning through states until reaching the END state.

        This method logs the start and end of the FSM run and handles exceptions that occur
        during state transitions.

        Parameters:
        continuous (bool): If True, run continuously until the END state is reached.
                        If False, run one step at a time and return True if the loop is not done, False if it is done.
        """
        if continuous : self.logger.info("Starting FSM run.")
        while self.current_state != self.States.END:
            self.logger.debug("Current state: %s", self.current_state)
            try:
                self.current_state = self.fsm()
            except AttributeError as e:
                self.logger.error(f"AttributeError in state {self.current_state}: {e}")
                break
            except TypeError as e:
                self.logger.error(f"TypeError in state {self.current_state}: {e}")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in state {self.current_state}: {e}")
                break

            if not continuous:
                return self.current_state == self.States.END

        self.logger.info("FSM run completed.")
        return True


    def fsm(self) -> Type[BaseState]:
        """
        Define the FSM logic.

        This method dynamically searches for a method that matches the name of the current state 
        and executes it. If the method is not found, it logs an error and transitions to the END state.

        Returns:
            BaseState: The next state of the FSM.
        """
        if not hasattr(self, 'current_state') or not self.current_state:
            self.logger.error("No current state defined.")
            return self.States.END
        self.logger.debug("Handling state: %s", self.current_state)

        # Get the method name from the current state
        method_name = self.current_state.name

        # Check if the method exists in the instance
        method = getattr(self, method_name, None)
        
        if method is None:
            self.logger.error(f"No method defined for state {self.current_state}.")
            return self.States.END
        
        try:
            self.logger.debug("Executing method for state: %s", self.current_state)
            return method()
        except Exception as e:
            self.logger.error(f"Error executing method for state {self.current_state}: {e}")
            return self.States.END
