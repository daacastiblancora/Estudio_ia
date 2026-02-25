"""
============================================================================
 COPILOTO OPERATIVO — Integration Test Suite
 ============================================================================
 Flujo completo de pruebas end-to-end:
   Fase 1: Ingesta de documentos (PDF)
   Fase 2: RAG + Validación de citaciones
   Fase 3: Tools de ejecución + Memoria conversacional
 ============================================================================
 Uso:
   python tests/test_integration.py
   # o con pytest:
   pytest tests/test_integration.py -v -s
 ============================================================================
"""

import os
import re
import sys
import uuid
import time
import requests
from datetime import datetime
from typing import Optional, Tuple

# ── Configuration ──────────────────────────────────────────────────────────

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8001/api/v1")
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "..", "documents")

# Test documents (must exist in /documents)
TEST_PDFS = [
    "TARIFAS 11 MAYO.pdf",
    "GitLab_Remote_Work.pdf",
]

# Unique session for memory continuity across tests
TEST_SESSION_ID = str(uuid.uuid4())

# Test user credentials
TEST_EMAIL = f"qa_tester_{uuid.uuid4().hex[:6]}@copiloto.com"
TEST_PASSWORD = "testpass1234"


# ── Logging Helpers ────────────────────────────────────────────────────────

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def log_phase(phase: str, description: str):
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {phase}: {description}{Colors.END}")
    print(f"{'='*70}")


def log_test(name: str, passed: bool, detail: str = ""):
    icon = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {icon}  {name}")
    if detail:
        print(f"        → {detail}")


def log_info(msg: str):
    print(f"  {Colors.YELLOW}ℹ️  {msg}{Colors.END}")


def log_agent_response(answer: str, max_len: int = 200):
    preview = answer[:max_len] + "..." if len(answer) > max_len else answer
    print(f"  {Colors.CYAN}🤖 Agent: {preview}{Colors.END}")


# ── Test State ─────────────────────────────────────────────────────────────

class TestState:
    """Shared state across test phases."""
    token: Optional[str] = None
    session_id: str = TEST_SESSION_ID
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: list = []

    @classmethod
    def record(cls, name: str, passed: bool, detail: str = ""):
        log_test(name, passed, detail)
        if passed:
            cls.passed += 1
        else:
            cls.failed += 1
            cls.errors.append(name)


state = TestState()


# ── Auth Helper ────────────────────────────────────────────────────────────

def setup_auth() -> Optional[str]:
    """Register a test user and return JWT token."""
    log_info(f"Registering test user: {TEST_EMAIL}")
    try:
        resp = requests.post(
            f"{BASE_URL}/register",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
            timeout=10,
        )
        if resp.status_code == 200:
            token = resp.json().get("access_token")
            log_info(f"Token obtained: {token[:20]}...")
            return token
        elif resp.status_code == 400:
            # User exists, try login
            log_info("User exists, logging in...")
            resp = requests.post(
                f"{BASE_URL}/login",
                data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
                timeout=10,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token")
        log_info(f"Auth failed: {resp.status_code} - {resp.text}")
        return None
    except Exception as e:
        log_info(f"Auth error: {e}")
        return None


def auth_headers() -> dict:
    """Return headers with JWT token."""
    return {"Authorization": f"Bearer {state.token}"}


# ── Chat Helper ────────────────────────────────────────────────────────────

def send_chat(query: str, session_id: Optional[str] = None, retries: int = 2) -> Tuple[Optional[dict], Optional[str]]:
    """
    Send a chat query and return (response_dict, error_string).
    Retries on timeout/5xx errors.
    """
    payload = {"query": query}
    if session_id:
        payload["session_id"] = session_id

    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                headers=auth_headers(),
                timeout=120,  # LLM can be slow
            )
            if resp.status_code == 200:
                return resp.json(), None
            elif resp.status_code >= 500 and attempt < retries:
                log_info(f"Server error (attempt {attempt+1}), retrying...")
                time.sleep(2)
                continue
            else:
                return None, f"HTTP {resp.status_code}: {resp.text[:200]}"
        except requests.Timeout:
            if attempt < retries:
                log_info(f"Timeout (attempt {attempt+1}), retrying...")
                time.sleep(2)
                continue
            return None, "Request timed out after 120s"
        except Exception as e:
            return None, str(e)

    return None, "Max retries exceeded"


# ══════════════════════════════════════════════════════════════════════════
#  FASE 1: INGESTA DE DATOS
# ══════════════════════════════════════════════════════════════════════════

def test_phase1_ingestion():
    log_phase("FASE 1", "Ingesta de Datos (Pipeline ETL)")

    for pdf_name in TEST_PDFS:
        pdf_path = os.path.join(DOCUMENTS_DIR, pdf_name)

        # Test: File exists
        exists = os.path.exists(pdf_path)
        state.record(f"File exists: {pdf_name}", exists, pdf_path if not exists else "")
        if not exists:
            continue

        # Test: Ingest endpoint
        try:
            with open(pdf_path, "rb") as f:
                resp = requests.post(
                    f"{BASE_URL}/ingest",
                    files={"file": (pdf_name, f, "application/pdf")},
                    timeout=120,
                )

            success = resp.status_code == 200
            data = resp.json() if success else {}
            chunks = data.get("chunks_created", 0)

            state.record(
                f"Ingest {pdf_name}",
                success and chunks > 0,
                f"HTTP {resp.status_code}, {chunks} chunks" if success else f"HTTP {resp.status_code}",
            )
        except Exception as e:
            state.record(f"Ingest {pdf_name}", False, f"Exception: {e}")


# ══════════════════════════════════════════════════════════════════════════
#  FASE 2: MOTOR RAG + VALIDACIÓN DE CITACIONES
# ══════════════════════════════════════════════════════════════════════════

def test_phase2_rag_and_citations():
    log_phase("FASE 2", "Motor RAG + Validación de Citaciones")

    if not state.token:
        log_info("SKIPPING: No auth token available")
        state.skipped += 1
        return

    # ── Test 2.1: Pregunta específica sobre tarifas ──
    query = "¿Cuál es el valor de la chequera de 30 hojas para persona natural?"
    log_info(f"Query: {query}")

    data, error = send_chat(query, session_id=state.session_id)

    if error:
        state.record("RAG query responds", False, error)
        return

    answer = data.get("answer", "")
    session = data.get("session_id", "")
    log_agent_response(answer)

    # Test: Got a response
    state.record("RAG query responds", bool(answer), f"session_id: {session[:12]}...")

    # Test: Session ID returned
    state.record("Session ID returned", bool(session), session[:12] if session else "None")

    # Test: Answer contains relevant content (tarifa-related words)
    tariff_keywords = ["chequera", "275", "persona", "natural", "costo", "tarifa", "valor"]
    found_keywords = [kw for kw in tariff_keywords if kw.lower() in answer.lower()]
    state.record(
        "Answer contains tariff data",
        len(found_keywords) >= 2,
        f"Keywords found: {found_keywords}",
    )

    # Test: Citation format validation
    # Primary: [File - Página X]
    # Legacy:  [File, Pág. X] or [File, Página X]
    citation_patterns = [
        r"\[.+?\s*-\s*Página\s*\d+\]",
        r"\[.+?\s*-\s*Pág\.?\s*\d+\]",
        r"\[.+?,\s*Pág\.?\s*\d+\]",
        r"\[.+?,\s*Página\s*\d+\]",
    ]

    citations_found = []
    for pattern in citation_patterns:
        matches = re.findall(pattern, answer)
        citations_found.extend(matches)

    has_citation = len(citations_found) > 0
    state.record(
        "Citation in correct format",
        has_citation,
        f"Found: {citations_found[:3]}" if has_citation else "No citations detected (intermittent — may be LLM-dependent)",
    )

    # ── Test 2.2: Pregunta sin respuesta (anti-alucinación) ──
    query2 = "¿Cuál es el color del edificio principal de la sede en Marte?"
    log_info(f"Query (hallucination test): {query2}")

    data2, error2 = send_chat(query2, session_id=state.session_id)

    if error2:
        state.record("Anti-hallucination responds", False, error2)
        return

    answer2 = data2.get("answer", "")
    log_agent_response(answer2)

    refusal_phrases = [
        "no tengo información",
        "no encontré",
        "no tengo datos",
        "documentos disponibles",
        "documentos internos",
    ]
    refused = any(phrase in answer2.lower() for phrase in refusal_phrases)
    state.record(
        "Anti-hallucination guardrail",
        refused,
        "Agent refused appropriately" if refused else "Agent may have hallucinated!",
    )


# ══════════════════════════════════════════════════════════════════════════
#  FASE 3: TOOLS DE EJECUCIÓN + MEMORIA CONVERSACIONAL
# ══════════════════════════════════════════════════════════════════════════

def test_phase3_tools_and_memory():
    log_phase("FASE 3", "Tools de Ejecución + Memoria Conversacional")

    if not state.token:
        log_info("SKIPPING: No auth token available")
        state.skipped += 1
        return

    # ── 3.1: generate_summary ──
    log_info("Test 3.1: generate_summary")
    query_summary = "Hazme un resumen ejecutivo de las tarifas del documento de mayo."
    data, error = send_chat(query_summary, session_id=state.session_id)

    if error:
        state.record("generate_summary activates", False, error)
    else:
        answer = data.get("answer", "")
        log_agent_response(answer)
        summary_keywords = ["resumen", "tarifa", "costo", "servicio", "punto"]
        found = [kw for kw in summary_keywords if kw.lower() in answer.lower()]
        state.record(
            "generate_summary activates",
            len(found) >= 2,
            f"Keywords: {found}",
        )

    # ── 3.2: generate_procedure ──
    log_info("Test 3.2: generate_procedure")
    query_proc = "Basándote en lo anterior, genera un procedimiento paso a paso para la solicitud de una chequera."
    data, error = send_chat(query_proc, session_id=state.session_id)

    if error:
        state.record("generate_procedure activates", False, error)
    else:
        answer = data.get("answer", "")
        log_agent_response(answer)
        proc_keywords = ["paso", "procedimiento", "1.", "2.", "solicitud", "chequera", "objetivo"]
        found = [kw for kw in proc_keywords if kw.lower() in answer.lower()]
        state.record(
            "generate_procedure activates",
            len(found) >= 2,
            f"Keywords: {found}",
        )

    # ── 3.3: create_task ──
    log_info("Test 3.3: create_task")
    query_task = "Crea una tarea con el título 'Revisar procedimiento de chequeras', descripción 'Validar el procedimiento generado', asignada a QA Team, prioridad alta."
    data, error = send_chat(query_task, session_id=state.session_id)

    if error:
        state.record("create_task activates", False, error)
    else:
        answer = data.get("answer", "")
        log_agent_response(answer)
        task_keywords = ["tarea", "creada", "revisar", "id", "éxito"]
        found = [kw for kw in task_keywords if kw.lower() in answer.lower()]
        state.record(
            "create_task activates",
            len(found) >= 2,
            f"Keywords: {found}",
        )

    # ── 3.4: list_tasks ──
    log_info("Test 3.4: list_tasks")
    query_list = "¿Cuáles son mis tareas pendientes?"
    data, error = send_chat(query_list, session_id=state.session_id)

    if error:
        state.record("list_tasks activates", False, error)
    else:
        answer = data.get("answer", "")
        log_agent_response(answer)
        list_keywords = ["tarea", "pendiente", "revisar", "chequera", "alta"]
        found = [kw for kw in list_keywords if kw.lower() in answer.lower()]
        state.record(
            "list_tasks activates",
            len(found) >= 2,
            f"Keywords: {found}",
        )

    # ── 3.5: Memory validation ──
    log_info("Test 3.5: Memory (session continuity)")
    query_memory = "¿De qué hemos hablado en esta conversación?"
    data, error = send_chat(query_memory, session_id=state.session_id)

    if error:
        state.record("Memory continuity", False, error)
    else:
        answer = data.get("answer", "")
        log_agent_response(answer)
        memory_keywords = ["tarifa", "chequera", "resumen", "procedimiento", "tarea"]
        found = [kw for kw in memory_keywords if kw.lower() in answer.lower()]
        state.record(
            "Memory continuity",
            len(found) >= 2,
            f"Agent remembers: {found}",
        )


# ══════════════════════════════════════════════════════════════════════════
#  REPORT
# ══════════════════════════════════════════════════════════════════════════

def print_report():
    total = state.passed + state.failed + state.skipped
    print(f"\n{'='*70}")
    print(f"{Colors.BOLD}  📊 TEST REPORT{Colors.END}")
    print(f"{'='*70}")
    print(f"  Total:    {total}")
    print(f"  {Colors.GREEN}Passed:   {state.passed}{Colors.END}")
    print(f"  {Colors.RED}Failed:   {state.failed}{Colors.END}")
    print(f"  {Colors.YELLOW}Skipped:  {state.skipped}{Colors.END}")
    print(f"  Session:  {state.session_id}")
    print(f"  Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if state.errors:
        print(f"\n  {Colors.RED}Failed tests:{Colors.END}")
        for e in state.errors:
            print(f"    ❌ {e}")

    print(f"{'='*70}\n")

    return state.failed == 0


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{Colors.BOLD}🚀 Copiloto Operativo — Integration Test Suite{Colors.END}")
    print(f"   Base URL:   {BASE_URL}")
    print(f"   Session:    {TEST_SESSION_ID}")
    print(f"   Documents:  {DOCUMENTS_DIR}")

    # Health check
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        if resp.status_code != 200:
            print(f"\n{Colors.RED}❌ Server not healthy: HTTP {resp.status_code}{Colors.END}")
            sys.exit(1)
        log_info("Server health: OK")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Server unreachable: {e}{Colors.END}")
        print(f"   Make sure the server is running: uvicorn app.main:app --port 8001")
        sys.exit(1)

    # Auth setup
    state.token = setup_auth()
    if not state.token:
        print(f"\n{Colors.RED}❌ Authentication failed, cannot proceed{Colors.END}")
        sys.exit(1)

    # Run phases
    test_phase1_ingestion()
    test_phase2_rag_and_citations()
    test_phase3_tools_and_memory()

    # Report
    all_passed = print_report()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
