#!/usr/bin/env python3
"""Core-only, side-effect-free initial KB bootstrap recipe renderer."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION="initial_kb_bootstrap_v1"
OPTIONAL_ADAPTER_STATES={"available","unavailable"}


def evaluate_case(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("clean_bootstrap") is not True or not isinstance(payload.get("optional_skills"),list):
        raise ValueError("INITIAL_KB_INPUT_INVALID")
    return {"schema_version":SCHEMA_VERSION,"recipe":"initial_kb_bootstrap","runnable":True,"product_implementation_claim":False}


def build_packet(payload: dict[str, Any]) -> dict[str, Any]:
    required={"project_root","raw_objective","authority_refs","output_target","goal_presence"}
    if not required.issubset(payload) or not str(payload.get("raw_objective","")).strip():
        raise ValueError("INITIAL_KB_PACKET_INPUT_MISSING")
    goal=payload["goal_presence"]
    if goal not in {"missing","existing","conflict"}: raise ValueError("INITIAL_KB_GOAL_STATE_INVALID")
    adapter_state=payload.get("optional_adapter_state","unavailable")
    if adapter_state not in OPTIONAL_ADAPTER_STATES:
        raise ValueError("INITIAL_KB_ADAPTER_STATE_INVALID")
    adapter=payload.get("optional_adapter","doc-system-kb-builder")
    if not isinstance(adapter,str) or not adapter.strip():
        raise ValueError("INITIAL_KB_ADAPTER_IDENTITY_INVALID")
    route={"missing":"goal_required","existing":"resume_goal","conflict":"human_decision"}[goal]
    return {
        "schema_version":SCHEMA_VERSION,"recipe":"initial_kb_bootstrap","project_root":payload["project_root"],"raw_objective":payload["raw_objective"],
        "authority_refs":payload["authority_refs"],"output_target":payload["output_target"],"classifier":{"goal_presence":goal,"route":route,"builder_allowed":False},
        "preflight":{"optional_adapter":{"extension_id":adapter,"availability":adapter_state,"required":False},"fallback":"extension" if adapter_state=="available" else "core_recipe"},
        "recipe_steps":["freeze_goal_authority","create_canonical_json_source","render_reader_projection","record_provenance_and_limitations","prepare_validation_handoff","write_chinese_closeout"],
        "minimum_delivery":["canonical JSON source","deterministic reader projection","provenance and limitations"],
        "required_lanes":["design","builder","validation","closure"],"write_exclusions":["product facts without source authority","external publication","automatic Builder start"],
        "validation_contract":"independent Validation recomputes from durable inputs","closeout_contract":"Dashboard records execution evidence; KB retains stable truth",
        "non_goals":["business ontology generation","product KB implementation","optional Skill installation","release or promotion"],
        "maximum_claim":"runnable core recipe packet; no product implementation claim","product_implementation_claim":False,
    }


def validate_packet(packet: dict[str,Any]) -> tuple[bool,str]:
    required={"schema_version","recipe","project_root","raw_objective","authority_refs","output_target","classifier","preflight","recipe_steps","minimum_delivery","required_lanes","write_exclusions","validation_contract","closeout_contract","non_goals","maximum_claim","product_implementation_claim"}
    if not required.issubset(packet) or packet.get("schema_version")!=SCHEMA_VERSION: return False,"INITIAL_KB_PACKET_INVALID"
    if packet["classifier"].get("goal_presence")=="missing" and packet["classifier"].get("route")!="goal_required": return False,"INITIAL_KB_GOAL_ROUTE_UNSAFE"
    adapter=packet.get("preflight",{}).get("optional_adapter",{})
    if adapter.get("availability") not in OPTIONAL_ADAPTER_STATES or not adapter.get("extension_id"):
        return False,"INITIAL_KB_ADAPTER_STATE_INVALID"
    if packet.get("product_implementation_claim") is not False: return False,"INITIAL_KB_OVERCLAIM"
    return True,"ok"


def render(packet: dict[str,Any]) -> str:
    ok,code=validate_packet(packet)
    if not ok: raise ValueError(code)
    return "\n".join(["# 初始 KB 受治理交接",f"\n原始目标：{packet['raw_objective']}",f"\nGoal 路由：`{packet['classifier']['route']}`；在 Goal 冻结且门禁满足前不得启动 Builder。","\n最小交付："]+[f"- {x}" for x in packet["minimum_delivery"]]+["\n必需 lanes："]+[f"- {x}" for x in packet["required_lanes"]]+["\n明确非目标："]+[f"- {x}" for x in packet["non_goals"]]+[f"\n声明上限：{packet['maximum_claim']}"])+"\n"


def _load(path:str)->dict[str,Any]: return json.load(sys.stdin) if path=="-" else json.loads(Path(path).read_text(encoding="utf-8"))


def main()->int:
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="command",required=True)
    for name in ("build","validate","render"):
        cmd=sub.add_parser(name); cmd.add_argument("input"); cmd.add_argument("--output")
    a=p.parse_args()
    try:
        data=_load(a.input); packet=build_packet(data) if a.command=="build" else data
        if a.command=="validate":
            ok,code=validate_packet(packet); print(json.dumps({"verdict":"pass" if ok else "fail","fingerprint":code},ensure_ascii=False)); return 0 if ok else 1
        output=json.dumps(packet,ensure_ascii=False,indent=2,sort_keys=True)+"\n" if a.command=="build" else render(packet)
        if a.output:
            target=Path(a.output)
            if target.exists(): raise ValueError("INITIAL_KB_OUTPUT_EXISTS")
            target.write_text(output,encoding="utf-8")
        else: print(output,end="")
        return 0
    except (OSError,json.JSONDecodeError,ValueError) as exc:
        print(json.dumps({"verdict":"fail","fingerprint":str(exc)},ensure_ascii=False)); return 1


if __name__=="__main__": raise SystemExit(main())
