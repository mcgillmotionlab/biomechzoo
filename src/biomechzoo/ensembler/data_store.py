import numpy as np
import re

from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload

from src.helpers import match_condition, extract_subject_id, extract_events, ZooEvent, ConditionSource, ConditionSpec


class DataStore:
    """
    Loads, indexes and extracts relevant data and information from the zoo files.
    """
    def __init__(self, fld, condition_spec: ConditionSpec | None=None, events=None, subj_list=None, str_match=None):
        self.fld = fld
        self.condition_spec = condition_spec or ConditionSpec(
            source=ConditionSource.FOLDER, conditions=[]
        )
        self.conditions = self.condition_spec.conditions
        self.subj_list = subj_list
        self.event_list = events
        self.str_match = str_match
        self._fl = engine(self.fld)
        self.subjects = self._resolve_subjects()


        # lazy caches — populated on first access
        self._extracted: set[tuple[str, str]] = set()
        self._lines: dict[tuple[str, str], list[np.ndarray]] = {}
        self._events: dict[tuple[str, str, str], list[ZooEvent]] = {}
        self._subj_index: dict[tuple[str, str], list[str]] = {}
        self._event_subj_index: dict[tuple[str, str, str], list[str]] = {}


    def _ensure_extracted(self, channel: str, condition: str) -> None:
        key = (channel, condition)
        if key not in self._extracted:
            self._extract(channel, condition)
            self._extracted.add(key)

    def get_lines(self, channel, condition):
        self._ensure_extracted(channel, condition)
        return self._lines.get((channel, condition), [])

    def get_events(self, channel, condition, event_name):
        self._ensure_extracted(channel, condition)

        event_key = (channel, condition, event_name)
        if event_key not in self._events:
            self._extract_events(channel, condition, event_name)
        return self._events.get(event_key, [])

    def get_subject_ids(self, channel, condition):
        self._ensure_extracted(channel, condition)
        return self._subj_index.get((channel, condition), [])



    def _extract(self, channel, condition):
        """Parse all zoo files for on (channel, condition) pair."""
        key = (channel,condition)
        self._lines[key] = []
        self._subj_index[key] = []

        zoo_channel = self._resolve_zoo_channel(channel, condition)

        for f in self._fl:
            data = zload(f)

            if self.condition_spec.source == ConditionSource.FOLDER:
                matched = match_condition(f, self.conditions)
                # fall save: condition needs to be all or match the condition currently in favour
                if matched != "__all__":
                    if matched != condition:
                        continue

            # fail save: key must be in data.
            if zoo_channel not in data.keys():
                continue

            subj = extract_subject_id(f, subj_list=self.subj_list, str_pattern=self.str_match)
            if subj is None:
                continue

            ch_data = data[zoo_channel]
            raw = ch_data.get("line")
            if raw is not None:
                arr = np.asarray(raw, dtype=float).squeeze()
                self._lines[key].append(arr)
                self._subj_index[key].append(subj)


    def get_event_values(self, channel: str, condition: str, event_name: str) -> list[float]:
        """Convenience — y-only, for violin/stats renderers."""
        return [ev.y for ev in self.get_events(channel, condition, event_name)]

    def _extract_events(self, channel, condition, event_name):
        """Separate pass for events. Only runs when events are needed"""
        event_key = (channel, condition, event_name)
        self._events[event_key] = []
        self._event_subj_index[event_key] = []

        zoo_channel = self._resolve_zoo_channel(channel, condition)

        for f in self._fl:
            data = zload(f)

            # Condition matching - branch on source type
            if self.condition_spec.source == ConditionSource.FOLDER:
                matched = match_condition(f, self.conditions)
                # fall save: condition needs to be all or match the condition currently in favour
                if matched != "__all__":
                    if matched != condition:
                        continue

            if zoo_channel not in data.keys():
                continue

            subj = extract_subject_id(f, subj_list=self.subj_list, str_pattern=self.str_match)
            if subj is None:
                continue

            val = extract_events(data[zoo_channel], event_name)
            if val is not None:
                self._events[event_key].append(val)
                self._event_subj_index[event_key].append(subj)


    def get_event_subject_ids(self, channel, condition, event_name):
        event_key = (channel, condition, event_name)
        if event_key not in self._events:
            self._extract_events(channel, condition, event_name)
        return self._event_subj_index.get(event_key, [])

    def _resolve_zoo_channel(self, channel, condition):
        """
        Returns the actual key to look up in the zoo dict.
        - FOLDER source  → channel name is used as-is
        - CHANNEL source → look up from channel_map
        """
        if self.condition_spec.source == ConditionSource.CHANNEL:
            return self.condition_spec.channel_map.get(condition, channel)
        return channel


    def _resolve_subjects(self):
        seen, result = set(), []
        for f in self._fl:
            matched = match_condition(f, self.conditions)
            if matched is None:
                continue

            subj =  extract_subject_id(f, subj_list=self.subj_list, str_pattern=self.str_match)
            if subj is None:
                continue

            if subj not in seen:
                seen.add(subj)
                result.append(subj)

        return result