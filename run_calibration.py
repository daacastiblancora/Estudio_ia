"""
run_calibration.py — Ejecuta las 20 preguntas de calibración contra el API del Copiloto
y genera un informe con la calificación de cada respuesta.

Uso:
    1. Asegurarse de que el servidor esté corriendo: uvicorn app.main:app --port 8001
    2. Ejecutar: python run_calibration.py
"""
import json
import re
import time
from datetime import datetime
import httpx

BASE_URL = "http://localhost:8001/api/v1"
TEST_USER_EMAIL = "calibracion@test.com"
TEST_USER_PASSWORD = "CalibTest2026!"

# ============================================================================
# QUESTION SET: 20 questions with expected answers and source PDFs
# ============================================================================
QUESTIONS = [
    # A. Exact Data (BM25 test)
    {
        "id": 1,
        "category": "A. Dato Exacto (BM25)",
        "question": "¿Cuánto cuesta el tour 'Colombia Corazón' de 15 días?",
        "expected_values": ["3.000", "USD", "13.950.000", "COP"],
        "expected_source": "01_colombia_corazon",
        "multi_turn": False,
    },
    {
        "id": 2,
        "category": "A. Dato Exacto (BM25)",
        "question": "¿Cuántos días dura el plan 'Colombia Armonía'?",
        "expected_values": ["8 días", "8 dias"],
        "expected_source": "04_colombia_armonia",
        "multi_turn": False,
    },
    {
        "id": 3,
        "category": "A. Dato Exacto (BM25)",
        "question": "¿Cuál es el precio del Plan Eje Cafetero Extremo?",
        "expected_values": ["3.720.000", "COP"],
        "expected_source": "07_eje_cafetero_extremo",
        "multi_turn": False,
    },
    {
        "id": 4,
        "category": "A. Dato Exacto (BM25)",
        "question": "¿Qué aerolíneas vuelan de México a Colombia?",
        "expected_values": ["Aeroméxico", "Avianca", "Copa"],
        "expected_source": "15_homepage_faq",
        "multi_turn": False,
    },
    {
        "id": 5,
        "category": "A. Dato Exacto (BM25)",
        "question": "¿Cuál es el requisito de vigencia del pasaporte para entrar a Colombia?",
        "expected_values": ["seis meses", "6 meses", "seis (6)"],
        "expected_source": "requisitos",
        "multi_turn": False,
    },
    # B. Semantic Search (RAG test)
    {
        "id": 6,
        "category": "B. Semántica (RAG)",
        "question": "¿Qué actividades turísticas puedo hacer en Cartagena de Indias?",
        "expected_values": ["Castillo", "San Felipe", "Islas del Rosario"],
        "expected_source": "",
        "multi_turn": False,
    },
    {
        "id": 7,
        "category": "B. Semántica (RAG)",
        "question": "Según el tour Colombia Corazón de 15 días, ¿qué incluye el paquete?",
        "expected_values": ["vuelos", "alojamiento", "desayuno"],
        "expected_source": "01_colombia_corazon",
        "multi_turn": False,
    },
    {
        "id": 8,
        "category": "B. Semántica (RAG)",
        "question": "¿Cuál es la mejor época para visitar Caño Cristales?",
        "expected_values": ["junio", "noviembre"],
        "expected_source": "cano_cristales",
        "multi_turn": False,
    },
    {
        "id": 9,
        "category": "B. Semántica (RAG)",
        "question": "¿Dónde puedo ver ballenas en Colombia?",
        "expected_values": ["Pacífico", "Nuquí", "Bahía Málaga", "Buenaventura"],
        "expected_source": "ballenas",
        "multi_turn": False,
    },
    {
        "id": 10,
        "category": "B. Semántica (RAG)",
        "question": "¿Qué destinos puedo visitar en 8 días en Colombia?",
        "expected_values": ["Bogotá", "Medellín", "Cartagena"],
        "expected_source": "",
        "multi_turn": False,
    },
    # C. Citation Accuracy
    {
        "id": 11,
        "category": "C. Citación",
        "question": "¿Cuáles son las normas ambientales para visitar Caño Cristales?",
        "expected_values": ["protector solar", "alga"],
        "expected_source": "cano_cristales",
        "multi_turn": False,
    },
    {
        "id": 12,
        "category": "C. Citación",
        "question": "¿Qué es el formulario Check-Mig y cuándo se debe llenar?",
        "expected_values": ["72 horas", "migra", "Check-Mig"],
        "expected_source": "requisitos",
        "multi_turn": False,
    },
    {
        "id": 13,
        "category": "C. Citación",
        "question": "¿Qué incluye y qué NO incluye el tour Colombia Corazón?",
        "expected_values": ["vuelos internacionales", "No incluye"],
        "expected_source": "01_colombia_corazon",
        "multi_turn": False,
    },
    {
        "id": 14,
        "category": "C. Citación",
        "question": "¿Cuánto cuesta un vuelo de México a Bogotá con Aeroméxico?",
        "expected_values": ["2,500", "2.500", "MXN"],
        "expected_source": "homepage_faq",
        "multi_turn": False,
    },
    {
        "id": 15,
        "category": "C. Citación",
        "question": "¿Qué ciudades se visitan en el plan Ritmo y Sabor?",
        "expected_values": ["Cali", "Medellín", "Cartagena"],
        "expected_source": "ritmo",
        "multi_turn": False,
    },
    # D. Multi-turn Memory
    {
        "id": 16,
        "category": "D. Memoria",
        "question": "¿Qué tours tienen disponibles para 4 días?",
        "expected_values": ["Eje Cafetero"],
        "expected_source": "",
        "multi_turn": True,
        "followup": "¿Cuánto cuesta el más barato de esos tours?",
        "followup_expected": ["3.380", "3380"],
    },
    {
        "id": 17,
        "category": "D. Memoria",
        "question": "¿Quién es Ana Echavarria?",
        "expected_values": ["travel planner", "planner", "Travel Planner"],
        "expected_source": "ana",
        "multi_turn": True,
        "followup": "¿En qué se especializa?",
        "followup_expected": ["especiali"],
    },
    {
        "id": 18,
        "category": "D. Memoria",
        "question": "Quiero ir a Medellín, ¿qué puedo hacer allá?",
        "expected_values": ["Medellín"],
        "expected_source": "",
        "multi_turn": True,
        "followup": "¿Qué paquetes de viaje incluyen esa ciudad?",
        "followup_expected": ["Colombia"],
    },
    {
        "id": 19,
        "category": "D. Memoria",
        "question": "¿Cómo llego a Colombia desde México?",
        "expected_values": ["Aeroméxico", "Avianca"],
        "expected_source": "",
        "multi_turn": True,
        "followup": "¿Cuál es la aerolínea más barata?",
        "followup_expected": ["2,500", "2.500", "VivaAerobus", "Viva"],
    },
    {
        "id": 20,
        "category": "D. Memoria",
        "question": "¿Qué requisitos necesito para viajar a Colombia desde España?",
        "expected_values": ["pasaporte", "visa"],
        "expected_source": "requisitos",
        "multi_turn": True,
        "followup": "¿Necesito visa?",
        "followup_expected": ["no necesit", "no requiere", "sin visa", "90 días", "no"],
    },
]


def register_user(client: httpx.Client) -> str:
    """Register a test user and return JWT token."""
    # Try to register
    resp = client.post(f"{BASE_URL}/register", json={
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    })
    
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"✅ Usuario de test registrado: {TEST_USER_EMAIL}")
        return token
    
    # If already registered, login
    resp = client.post(f"{BASE_URL}/login", data={
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    })
    
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"✅ Login exitoso: {TEST_USER_EMAIL}")
        return token
    
    raise Exception(f"❌ No se pudo autenticar: {resp.status_code} — {resp.text}")


def ask_question(client: httpx.Client, token: str, question: str, session_id: str = None) -> dict:
    """Send a question to the chat endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    body = {"query": question}
    if session_id:
        body["session_id"] = session_id
    
    resp = client.post(f"{BASE_URL}/chat", json=body, headers=headers, timeout=60)
    
    if resp.status_code != 200:
        return {"answer": f"ERROR {resp.status_code}: {resp.text}", "sources": [], "session_id": ""}
    
    return resp.json()


def check_values_in_answer(answer: str, expected_values: list) -> tuple:
    """Check how many expected values are found in the answer."""
    found = []
    missing = []
    answer_lower = answer.lower()
    
    for val in expected_values:
        if val.lower() in answer_lower:
            found.append(val)
        else:
            missing.append(val)
    
    return found, missing


def check_source_cited(answer: str, sources: list, expected_source: str) -> bool:
    """Check if the expected source PDF was cited."""
    if not expected_source:
        return True  # No specific source expected
    
    # Check in sources list
    for src in sources:
        doc_name = src.get("document_name", "").lower()
        if expected_source.lower() in doc_name:
            return True
    
    # Check in answer text
    if expected_source.lower() in answer.lower():
        return True
    
    return False


def has_any_citation(answer: str) -> bool:
    """Check if the answer contains any citation in bracket format."""
    patterns = [
        r"\[.*?\.pdf.*?\]",
        r"\[.*?Pág.*?\]",
        r"\[.*?Página.*?\]",
    ]
    for p in patterns:
        if re.search(p, answer):
            return True
    return False


def run_calibration():
    """Run the full calibration test suite."""
    print("=" * 70)
    print("🧪 CALIBRACIÓN COPILOTO OPERATIVO — ColombiaTours.Travel")
    print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 70)
    
    client = httpx.Client()
    
    # 1. Authenticate
    try:
        token = register_user(client)
    except Exception as e:
        print(f"\n❌ ERROR DE AUTENTICACIÓN: {e}")
        print("   Asegúrate de que el servidor esté corriendo: uvicorn app.main:app --port 8001")
        return
    
    # 2. Run questions
    results = []
    total_score = 0
    max_score = 0
    
    for i, q in enumerate(QUESTIONS):
        # Delay between questions to avoid rate limits (Groq + slowapi)
        if i > 0:
            print(f"\n    ⏱️ Esperando 5s...")
            time.sleep(5)
        
        print(f"\n{'─' * 60}")
        print(f"[{q['id']:02d}] {q['category']}")
        print(f"    Q: {q['question']}")
        
        # Ask main question
        response = ask_question(client, token, q["question"])
        answer = response.get("answer", "")
        sources = response.get("sources", [])
        session_id = response.get("session_id", "")
        
        print(f"    A: {answer[:150]}...")
        
        # Grade: Values
        found, missing = check_values_in_answer(answer, q["expected_values"])
        value_score = len(found) / len(q["expected_values"]) if q["expected_values"] else 1.0
        
        # Grade: Source
        source_cited = check_source_cited(answer, sources, q["expected_source"])
        has_citation = has_any_citation(answer)
        
        # Grade: Hallucination (basic — check "no tengo información" when there IS info)
        no_info_response = "no tengo información" in answer.lower() or "no encuentro" in answer.lower()
        
        # Score calculation
        q_score = 0
        q_max = 3  # Max 3 points per question
        
        if value_score >= 0.5:
            q_score += 1  # Found at least half the expected values
        if value_score >= 1.0:
            q_score += 1  # Found ALL expected values
        if has_citation or source_cited:
            q_score += 1  # Has some form of citation
        
        # Handle multi-turn questions
        followup_result = None
        if q.get("multi_turn") and q.get("followup"):
            q_max += 2  # Extra points for followup
            print(f"    Q2: {q['followup']}")
            
            time.sleep(1)  # Brief pause between turns
            fu_response = ask_question(client, token, q["followup"], session_id)
            fu_answer = fu_response.get("answer", "")
            
            print(f"    A2: {fu_answer[:150]}...")
            
            fu_found, fu_missing = check_values_in_answer(fu_answer, q.get("followup_expected", []))
            fu_score = len(fu_found) / len(q["followup_expected"]) if q.get("followup_expected") else 1.0
            
            if fu_score >= 0.5:
                q_score += 1
            if fu_score >= 1.0:
                q_score += 1
            
            followup_result = {
                "answer": fu_answer,
                "found": fu_found,
                "missing": fu_missing,
                "score": fu_score,
            }
        
        total_score += q_score
        max_score += q_max
        
        result = {
            "id": q["id"],
            "category": q["category"],
            "question": q["question"],
            "answer": answer,
            "expected_values": q["expected_values"],
            "found_values": found,
            "missing_values": missing,
            "value_score": value_score,
            "source_cited": source_cited,
            "has_citation": has_citation,
            "no_info_response": no_info_response,
            "q_score": q_score,
            "q_max": q_max,
            "followup": followup_result,
        }
        results.append(result)
        
        # Print grade
        grade = "✅" if q_score >= q_max * 0.7 else "⚠️" if q_score >= q_max * 0.4 else "❌"
        print(f"    {grade} Puntuación: {q_score}/{q_max} | Valores: {len(found)}/{len(q['expected_values'])} | Citación: {'✅' if has_citation else '❌'}")
    
    # 3. Generate report
    pct = (total_score / max_score * 100) if max_score > 0 else 0
    
    print(f"\n{'=' * 70}")
    print(f"📊 RESULTADO FINAL: {total_score}/{max_score} ({pct:.1f}%)")
    print(f"   {'✅ APROBADO' if pct >= 85 else '❌ NO APROBADO'} (umbral: 85%)")
    print(f"{'=' * 70}")
    
    # Generate markdown report
    generate_report(results, total_score, max_score, pct)
    
    client.close()


def generate_report(results, total_score, max_score, pct):
    """Generate the calibration report in markdown format."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = [
        f"# Informe de Calibración — Copiloto Operativo",
        f"",
        f"**Fecha:** {now}",
        f"**Corpus:** 20 PDFs de colombiatours.travel",
        f"**Resultado:** {total_score}/{max_score} ({pct:.1f}%)",
        f"**Estado:** {'✅ APROBADO' if pct >= 85 else '❌ NO APROBADO (requiere iteración)'}",
        f"",
        f"---",
        f"",
        f"## Resultados por Pregunta",
        f"",
        f"| # | Categoría | Pregunta | Valores | Citación | Score |",
        f"|---|---|---|---|---|---|",
    ]
    
    for r in results:
        grade = "✅" if r["q_score"] >= r["q_max"] * 0.7 else "⚠️" if r["q_score"] >= r["q_max"] * 0.4 else "❌"
        citation = "✅" if r["has_citation"] else "❌"
        vals = f"{len(r['found_values'])}/{len(r['expected_values'])}"
        q_short = r["question"][:60] + "..." if len(r["question"]) > 60 else r["question"]
        lines.append(f"| {r['id']} | {r['category']} | {q_short} | {vals} | {citation} | {grade} {r['q_score']}/{r['q_max']} |")
    
    lines.extend([
        f"",
        f"---",
        f"",
        f"## Análisis por Categoría",
        f"",
    ])
    
    # Group by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"score": 0, "max": 0, "count": 0}
        categories[cat]["score"] += r["q_score"]
        categories[cat]["max"] += r["q_max"]
        categories[cat]["count"] += 1
    
    for cat, data in categories.items():
        cat_pct = (data["score"] / data["max"] * 100) if data["max"] > 0 else 0
        lines.append(f"- **{cat}**: {data['score']}/{data['max']} ({cat_pct:.0f}%)")
    
    lines.extend([
        f"",
        f"---",
        f"",
        f"## Detalle de Respuestas",
        f"",
    ])
    
    for r in results:
        lines.append(f"### Pregunta {r['id']}: {r['question']}")
        lines.append(f"")
        lines.append(f"**Respuesta IA:**")
        lines.append(f"> {r['answer'][:500]}")
        lines.append(f"")
        lines.append(f"- Valores encontrados: {', '.join(r['found_values']) if r['found_values'] else 'Ninguno'}")
        lines.append(f"- Valores faltantes: {', '.join(r['missing_values']) if r['missing_values'] else 'Ninguno'}")
        lines.append(f"- ¿Citó fuente?: {'Sí' if r['has_citation'] else 'No'}")
        
        if r["followup"]:
            lines.append(f"")
            lines.append(f"**Followup:** {r['followup']['answer'][:300]}")
            lines.append(f"- Valores followup encontrados: {', '.join(r['followup']['found'])}")
        
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
    
    report_path = "informe_calibracion.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"\n📄 Informe guardado en: {report_path}")


if __name__ == "__main__":
    run_calibration()
