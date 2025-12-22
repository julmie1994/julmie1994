"""Scenario state machine for ICAO VFR training dialogs.

States are deterministic and describe expected slots plus allowed transitions.
LLMs are never used for state advancement; validation output drives progression.

Example usage:
    state = "initial_call"
    validation = {"ok": True}
    state = advance_state(state, validation, scenario="graz_vfr_sector_e")
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Optional


@dataclass(frozen=True)
class State:
    name: str
    required_slots: List[str]
    optional_slots: List[str]
    next_states: List[str]
    atc_templates: List[str]
    readback_required: bool
    readback_slots: List[str]


Scenario = Dict[str, State]


def _state(
    name: str,
    *,
    required_slots: Iterable[str],
    optional_slots: Iterable[str] = (),
    next_states: Iterable[str],
    atc_templates: Iterable[str],
    readback_required: bool = False,
    readback_slots: Iterable[str] = (),
) -> State:
    return State(
        name=name,
        required_slots=list(required_slots),
        optional_slots=list(optional_slots),
        next_states=list(next_states),
        atc_templates=list(atc_templates),
        readback_required=readback_required,
        readback_slots=list(readback_slots),
    )


SCENARIOS: Dict[str, Scenario] = {
    "graz_vfr_sector_e": {
        "initial_call": _state(
            "initial_call",
            required_slots=["callsign"],
            next_states=["taxi_request"],
            atc_templates=["{callsign}, Graz Tower"],
        ),
        "taxi_request": _state(
            "taxi_request",
            required_slots=["callsign", "position"],
            optional_slots=["qnh", "taxiway"],
            next_states=["taxi_clearance"],
            atc_templates=["Taxi to holding point runway {runway}, via {taxiway}, QNH {qnh}"],
        ),
        "taxi_clearance": _state(
            "taxi_clearance",
            required_slots=["callsign", "runway", "qnh"],
            optional_slots=["taxiway"],
            next_states=["intermediate_hold"],
            atc_templates=["Hold at intermediate stop {holding_point}, give way to {traffic}"],
            readback_required=True,
            readback_slots=["runway", "qnh", "holding_point"],
        ),
        "intermediate_hold": _state(
            "intermediate_hold",
            required_slots=["callsign", "holding_point"],
            next_states=["taxi_continue"],
            atc_templates=["Continue taxi to holding point {holding_point}"],
        ),
        "taxi_continue": _state(
            "taxi_continue",
            required_slots=["callsign", "holding_point"],
            optional_slots=["taxiway"],
            next_states=["departure_instructions"],
            atc_templates=[
                "Leave the control zone via VFR sector {sector}, {altitude} or below, "
                "right turn after departure, report ready for departure"
            ],
        ),
        "departure_instructions": _state(
            "departure_instructions",
            required_slots=["callsign", "sector", "altitude"],
            optional_slots=["runway"],
            next_states=["lineup_wait"],
            atc_templates=["Line up runway {runway} and wait"],
            readback_required=True,
            readback_slots=["sector", "altitude", "runway"],
        ),
        "lineup_wait": _state(
            "lineup_wait",
            required_slots=["callsign", "runway"],
            next_states=["takeoff_clearance"],
            atc_templates=["Wind {wind}, runway {runway}, cleared for takeoff"],
            readback_required=True,
            readback_slots=["runway", "wind"],
        ),
        "takeoff_clearance": _state(
            "takeoff_clearance",
            required_slots=["callsign", "runway", "wind"],
            next_states=["airborne_time"],
            atc_templates=["Airborne time {time}, report leaving sector {sector}"],
            readback_required=True,
            readback_slots=["runway", "wind"],
        ),
        "airborne_time": _state(
            "airborne_time",
            required_slots=["callsign", "time", "sector"],
            optional_slots=["altitude"],
            next_states=["qnh_update"],
            atc_templates=["New QNH {qnh}"],
        ),
        "qnh_update": _state(
            "qnh_update",
            required_slots=["callsign", "qnh"],
            next_states=["leave_sector"],
            atc_templates=["Report leaving sector {sector}"],
            readback_required=True,
            readback_slots=["qnh"],
        ),
        "leave_sector": _state(
            "leave_sector",
            required_slots=["callsign", "sector", "altitude"],
            optional_slots=["time"],
            next_states=["frequency_change"],
            atc_templates=["Approved to leave the frequency"],
        ),
        "frequency_change": _state(
            "frequency_change",
            required_slots=["callsign"],
            next_states=["end"],
            atc_templates=["Frequency change approved"],
        ),
        "end": _state(
            "end",
            required_slots=[],
            next_states=[],
            atc_templates=["End of scenario"],
        ),
    }
}


def get_state(state_name: str, *, scenario: str) -> Optional[State]:
    return SCENARIOS.get(scenario, {}).get(state_name)


def advance_state(
    current_state: str,
    validation: Mapping[str, object],
    *,
    scenario: str,
) -> str:
    """Advance to next state based on validation outcome.

    Rules:
    - If validation ok is True and a next state exists, advance to the first next state.
    - Otherwise stay in the current state.
    """
    state = get_state(current_state, scenario=scenario)
    if not state:
        return current_state
    ok = bool(validation.get("ok", False))
    if ok and state.next_states:
        return state.next_states[0]
    return current_state


if __name__ == "__main__":
    # Simple self-tests
    state = "initial_call"
    state = advance_state(state, {"ok": True}, scenario="graz_vfr_sector_e")
    assert state == "taxi_request", state

    state = advance_state(state, {"ok": False}, scenario="graz_vfr_sector_e")
    assert state == "taxi_request", state

    state = advance_state(state, {"ok": True}, scenario="graz_vfr_sector_e")
    assert state == "taxi_clearance", state

    print("State machine self-tests passed.")
