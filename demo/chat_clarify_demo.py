# # =========================================================
# # ===== file: demo/chat_clarify_demo.py
# # =========================================================
# from core.audit.logger import AuditLogger
# from core.engine import LatentFlowEngine
# from core.guard.state_guard import StateGuard
# from core.guard.rules import max_steps
# from core.infer.cost import CostCounter
# from core.verify.verifier import Verifier
#
# # from core.lang.pipeline import LanguagePipeline
# # from core.verify.policy import Policy
# # from core.verify.constraints_verifier import ConstraintsVerifier
# # from core.planner.constrained_planner import ConstrainedPlanner
# #
# # from core.executor.registry import ToolRegistry
# # from core.executor.executor_v2 import ToolExecutorV2
# # from core.runtime.meta_runtime import MetaRuntime
#
# from core.dialog.clarification import Clarifier
# from core.dialog.response_builder import ResponseBuilder
# from core.dialog.renderer import Renderer
#
#
# def main():
#     logger = AuditLogger(path=None, also_stdout=False)
#
#     engine = LatentFlowEngine(guard=StateGuard([max_steps(2000)]), verifier=Verifier(), audit_logger=logger)
#     state = engine.init()
#     cost = CostCounter()
#
#     lp = LanguagePipeline()
#     policy = Policy(max_transfer_amount=1000.0, require_approval_over=500.0, blocked_targets={"EvilGuy"})
#     planner = ConstrainedPlanner(verifier=ConstraintsVerifier(policy=policy))
#
#     reg = ToolRegistry()
#     reg.register("check_user", lambda user=None: {"exists": True})
#     reg.register("check_balance", lambda currency=None, amount=None: {"ok": True})
#     reg.register("create_transfer", lambda to=None, amount=None, currency=None: {"transfer_id": "T-1"})
#     reg.register("submit_transfer", lambda: {"submitted": True})
#     executor = ToolExecutorV2(registry=reg, audit_logger=logger)
#
#     rt = MetaRuntime(engine=engine, planner=planner, executor=executor, audit_logger=logger)
#
#     clarifier = Clarifier()
#     rb = ResponseBuilder()
#     r = Renderer()
#
#     # 模拟用户输入（故意触发澄清/冲突）
#     user_inputs = [
#         "给EvilGuy转账 100 元",
#         "给Alice转账 900 元，不要审批",
#         "给Bob转账",  # 缺槽位：amount
#         "给Bob转账 100 元",
#     ]
#
#     for text in user_inputs:
#         intent_block = lp.to_intent_blocks(text)[0]
#         state, res = rt.run(state=state, cost=cost, intent_block=intent_block)
#
#         if res.status == "OK":
#             msg = rb.render({
#                 "status": "OK",
#                 "intent": res.intent_frame.get("intent"),
#                 "slots": res.intent_frame.get("slots"),
#                 "executed_steps": res.executed or []
#             })
#             print("\nUSER:", text)
#             print("BOT:", r.concise(msg))
#             continue
#
#         # 失败/拒绝时尝试澄清
#         qs = []
#         qs += clarifier.questions_for_missing_slots(res.intent_frame)
#         qs += clarifier.questions_for_conflict(res.error or "")
#         status = "NEED_CLARIFICATION" if qs else "DENY"
#
#         msg = rb.render({
#             "status": status,
#             "reason": res.error,
#             "questions": qs
#         })
#
#         print("\nUSER:", text)
#         print("BOT:", r.concise(msg))
#
#     print("\nSTATE:", state.summary())
#     print("COST:", cost.summary())
#
#
# if __name__ == "__main__":
#     main()
