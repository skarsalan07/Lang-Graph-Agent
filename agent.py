from typing import TypedDict, Dict, Any, List
from langgraph.graph import StateGraph



# STATE SCHEMA (Shared Ticket Memory)

class TicketState(TypedDict, total=False):
    ticket_id: str
    customer_name: str
    email: str
    query: str
    priority: str

    # Progressive fields
    entities: Dict[str, Any]
    normalized_fields: Dict[str, Any]
    clarification: str
    user_answer: str
    kb_results: List[str]
    decision_score: int
    decision: Dict[str, Any]
    response: str
    final_status: str
    notifications_sent: bool


# MOCK MCP CLIENTS

class MCPClient:
    def __init__(self, name: str):
        self.name = name

    def call(self, ability: str, state: TicketState) -> Dict[str, Any]:
        """Simulate an ability execution routed to a MCP client"""
        print(f"[{self.name} MCP] Executing: {ability}")
        return {ability: f"mock_result_from_{self.name}"}


COMMON = MCPClient("COMMON")
ATLAS = MCPClient("ATLAS")



# STAGE FUNCTIONS (11 nodes)


# 1. Intake
def intake_node(state: TicketState) -> TicketState:
    print("Stage 1: INTAKE")
    COMMON.call("accept_payload \n", state)
    return state


# 2. Understand
def understand_node(state: TicketState) -> TicketState:
    print("Stage 2: UNDERSTAND")
    COMMON.call("parse_request_text", state)
    entities = ATLAS.call("extract_entities", state)  # API should return entities
    state["entities"] = entities
    print(f"Entities extracted: {state['entities']} \n")
    return state



# 3. Prepare
def prepare_node(state: TicketState) -> TicketState:
    print("Stage 3: PREPARE")
    COMMON.call("normalize_fields", state)
    ATLAS.call("enrich_records", state)
    COMMON.call("add_flags_calculations", state)

    pri = state.get("priority", "low").lower()
    mapping = {"low": 40, "medium": 70, "high": 90, "urgent": 100}
    score = mapping.get(pri, 50)
    state["normalized_fields"] = {"priority_score": score}
    print(f"Normalized fields: {state['normalized_fields']} \n")
    return state


# 4. Ask
def ask_node(state: TicketState) -> TicketState:
    print("Stage 4: ASK")
    ATLAS.call("clarify_question", state)
    state["clarification"] = "Could you provide your Order ID?"
    print(f"Clarification requested: {state['clarification']} \n")
    return state


# 5. Wait
def wait_node(state: TicketState) -> TicketState:
    print("Stage 5: WAIT")
    ATLAS.call("extract_answer", state)
    state["user_answer"] = "Order ID: 12345"  # mocked user response
    print(f"User answer stored: {state['user_answer']} \n")
    return state


# 6. Retrieve
def retrieve_node(state: TicketState) -> TicketState:
    print("Stage 6: RETRIEVE")
    ATLAS.call("knowledge_base_search", state)
    state["kb_results"] = ["FAQ: Orders may be delayed 5-7 days."]
    print(f"Knowledge base results: {state['kb_results']} \n")
    return state


# 7. Decide
def decide_node(state: TicketState) -> TicketState:
    print("Stage 7: DECIDE")
    COMMON.call("solution_evaluation", state)

    score = 82  # mocked demo score
    state["decision_score"] = score
    if score < 90:
        print("Low confidence → Escalating")
        ATLAS.call("escalation_decision", state)
        state["decision"] = {"escalated": True, "score": score}
    else:
        print("High confidence → Auto resolved")
        state["decision"] = {"auto_resolved": True, "score": score}

    COMMON.call("update_payload", state)
    print(f"Decision recorded: {state['decision']} \n")
    return state


# 8. Update
def update_node(state: TicketState) -> TicketState:
    print("Stage 8: UPDATE")
    ATLAS.call("update_ticket", state)
    ATLAS.call("close_ticket", state)
    state["final_status"] = "Closed"
    print(f"Final status: {state['final_status']} \n")
    return state


# 9. Create
def create_node(state: TicketState) -> TicketState:
    print("Stage 9: CREATE")
    COMMON.call("response_generation", state)
    if state.get("decision", {}).get("escalated"):
        msg = f"Hi {state['customer_name']}, your case has been escalated."
    else:
        msg = f"Hi {state['customer_name']}, we’ve resolved your issue."
    state["response"] = msg
    print(f"Response drafted: {state['response']} \n")
    return state


# 10. Do
def do_node(state: TicketState) -> TicketState:
    print("Stage 10: DO")
    ATLAS.call("execute_api_calls", state)
    ATLAS.call("trigger_notifications", state)
    state["notifications_sent"] = True
    print(f"Notifications sent: {state['notifications_sent']}")
    return state


# 11. Complete
def complete_node(state: TicketState) -> TicketState:
    print("Stage 11: COMPLETE")
    COMMON.call("output_payload", state)
    print("Final payload ready")
    return state



# GRAPH DEFINITION


graph = StateGraph(TicketState)

graph.add_node("INTAKE", intake_node)
graph.add_node("UNDERSTAND", understand_node)
graph.add_node("PREPARE", prepare_node)
graph.add_node("ASK", ask_node)
graph.add_node("WAIT", wait_node)
graph.add_node("RETRIEVE", retrieve_node)
graph.add_node("DECIDE", decide_node)
graph.add_node("UPDATE", update_node)
graph.add_node("CREATE", create_node)
graph.add_node("DO", do_node)
graph.add_node("COMPLETE", complete_node)

graph.set_entry_point("INTAKE")

graph.add_edge("INTAKE", "UNDERSTAND")
graph.add_edge("UNDERSTAND", "PREPARE")
graph.add_edge("PREPARE", "ASK")
graph.add_edge("ASK", "WAIT")
graph.add_edge("WAIT", "RETRIEVE")
graph.add_edge("RETRIEVE", "DECIDE")
graph.add_edge("DECIDE", "UPDATE")
graph.add_edge("UPDATE", "CREATE")
graph.add_edge("CREATE", "DO")
graph.add_edge("DO", "COMPLETE")

workflow = graph.compile()



# DEMO RUN


if __name__ == "__main__":
    input_ticket = TicketState(
        ticket_id="T12345",
        customer_name="Alice",
        email="alice@example.com",
        query="My order hasn’t arrived yet",
        priority="high"
    )

    print("Running LangGraph Customer Support Agent...\n")
    final_state = workflow.invoke(input_ticket)

    print("\n PAYLOAD  --> ")
    for k, v in final_state.items():
        print(f"{k}: {v}")
