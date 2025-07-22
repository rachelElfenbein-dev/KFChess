class StateMachine:
    def __init__(self, states: dict, initial: str):
        self.states = states
        self.current = states[initial]

    def process_command(self, cmd, now_ms):
        next_state= self.current.transitions.get(cmd.type)
        if next_state:   
            self.current = next_state
            self.current.reset(cmd)
        else:
            self.current.reset(cmd)
        self.current.update(now_ms)

    def update(self, now_ms):
        new_cmd = self.current.update(now_ms)
        if new_cmd:
            self.process_command(new_cmd, now_ms)