class EventLoop(object):

    def __init__(self, id: str, events: list = None) -> None:
        self.id = id
        self.events = [] if events is None else events
        self._current_events = {}
        self._future_events = {}
        for event_id in self.events:
            self.register_event(event_id)

    @property
    def event_data(self):
        return self._current_events

    def register_event(self, event_id: str):
        if event_id in self._current_events:
            raise ValueError(f"Event loop '{self.name}': duplicate event '{event_id}'")
        self._current_events[event_id] = False
        self._future_events[event_id] = False

    def produce(self, event_id: str) -> None:
        if event_id not in self._current_events:
            raise ValueError(
                "Event loop '{}': 'produce' request unrecognized event: {}".format(self.name, event_id))
        self._future_events[event_id] = True

    def consume(self, event_id: str):
        if event_id not in self._current_events:
            raise ValueError(
                "Event loop '{}': 'consume' request unrecognized event: {}".format(self.name, event_id))
        return self._current_events[event_id]

    def reconfigure(self):
        for event_id in self._future_events:
            self._current_events[event_id] = self._future_events[event_id]
            self._future_events[event_id] = False
