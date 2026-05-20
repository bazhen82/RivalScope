import json
from typing import Any, Dict, Optional

from openai import OpenAI

from backend.config import settings
from backend.models.schemas import AnalysisContext, AnalysisResult, ImageAnalysisResult


def _json_from_text(content: str) -> Dict[str, Any]:
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json\n", "", 1).replace("JSON\n", "", 1)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start : end + 1])
        raise


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value:
        return [str(value)]
    return []


def _score(value: Any) -> int:
    try:
        return max(0, min(10, int(float(value))))
    except (TypeError, ValueError):
        return 0


def _normalize_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    scores = data.get("scores") if isinstance(data.get("scores"), dict) else {}
    return {
        "summary": str(data.get("summary") or data.get("description") or "Анализ выполнен."),
        "strengths": _as_list(data.get("strengths")),
        "weaknesses": _as_list(data.get("weaknesses")),
        "unique_offers": _as_list(data.get("unique_offers")),
        "recommendations": _as_list(data.get("recommendations")),
        "scores": {str(key): _score(value) for key, value in scores.items()},
        "positioning_gap": _as_list(data.get("positioning_gap")),
        "action_plan": _as_list(data.get("action_plan")),
    }


def _normalize_image_analysis(data: Dict[str, Any]) -> Dict[str, Any]:
    scores = data.get("scores") if isinstance(data.get("scores"), dict) else {}
    return {
        "description": str(data.get("description") or data.get("summary") or "Изображение проанализировано."),
        "marketing_insights": _as_list(data.get("marketing_insights")),
        "visual_style_analysis": str(data.get("visual_style_analysis") or "Визуальный стиль требует дополнительной оценки."),
        "recommendations": _as_list(data.get("recommendations")),
        "scores": {str(key): _score(value) for key, value in scores.items()},
        "animation_potential": str(data.get("animation_potential") or ""),
    }


class AIService:
    def __init__(self) -> None:
        self.client: Optional[OpenAI] = None
        if settings.proxy_api_key:
            self.client = OpenAI(
                api_key=settings.proxy_api_key,
                base_url=settings.proxy_api_base_url,
            )

    @property
    def provider_name(self) -> str:
        if self.client:
            return "ProxyAPI"
        if settings.enable_gigachat_fallback and settings.gigachat_api_key:
            return "GigaChat fallback"
        return "not configured"

    def _context_text(self, context: AnalysisContext) -> str:
        return (
            f"Ниша: {context.effective_niche}\n"
            f"Мой бренд: {context.own_brand or 'не указан'}\n"
            f"Мой сайт: {context.own_site or 'не указан'}\n"
            f"Целевая аудитория: {context.target_audience or 'не указана'}"
        )

    def _chat_json(self, model: str, messages: list[dict[str, Any]]) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("ProxyAPI key is not configured. Add PROXY_API_KEY to .env.")

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.25,
            response_format={"type": "json_object"},
        )
        return _json_from_text(response.choices[0].message.content or "{}")

    async def analyze_text(self, text: str, context: AnalysisContext) -> AnalysisResult:
        system = """
Ты — senior-аналитик конкурентной разведки для малого и среднего бизнеса.
Ты анализируешь именно текстовый оффер/описание конкурента, а не сайт и не изображение.
Верни строго JSON без markdown. Ответ на русском языке.
Важно:
- Анализируй только объект, который пользователь передал после блока "Объект анализа".
- "Мой бренд" из контекста используй только как точку сравнения, но не называй им конкурента.
- Не оценивай визуальный дизайн или анимацию, если в тексте нет явных данных об этом.
Схема:
{
  "summary": "краткий вывод",
  "strengths": ["3-5 пунктов"],
  "weaknesses": ["3-5 пунктов"],
  "unique_offers": ["3-5 пунктов"],
  "recommendations": ["3-7 пунктов"],
  "scores": {
    "offer_score": 0-10,
    "differentiation_score": 0-10,
    "trust_score": 0-10,
    "content_clarity": 0-10,
    "conversion_potential": 0-10,
    "automation_relevance": 0-10
  },
  "positioning_gap": ["что можно усилить относительно рынка"],
  "action_plan": ["конкретные действия для владельца бренда"]
}
"""
        data = self._chat_json(
            settings.openai_model,
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"{self._context_text(context)}\n\nОбъект анализа:\n{text}",
                },
            ],
        )
        normalized = _normalize_analysis(data)
        return AnalysisResult(**normalized, raw=data)

    async def analyze_image(
        self,
        image_base64: str,
        mime_type: str,
        context: AnalysisContext,
    ) -> ImageAnalysisResult:
        system = """
Ты — эксперт по визуальному маркетингу, сайтам, баннерам и AI-автоматизации.
Проанализируй изображение конкурента. Верни строго JSON без markdown:
{
  "description": "что изображено",
  "marketing_insights": ["3-5 инсайтов"],
  "visual_style_analysis": "анализ визуального стиля",
  "recommendations": ["3-7 рекомендаций"],
  "scores": {
    "visual_style_score": 0-10,
    "clarity_score": 0-10,
    "trust_score": 0-10,
    "cta_score": 0-10,
    "animation_potential": 0-10
  },
  "animation_potential": "как можно усилить визуал через motion/анимацию"
}
"""
        if not self.client:
            raise RuntimeError("ProxyAPI key is not configured. Add PROXY_API_KEY to .env.")
        response = self.client.chat.completions.create(
            model=settings.openai_vision_model,
            temperature=0.25,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self._context_text(context)},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
        )
        data = _json_from_text(response.choices[0].message.content or "{}")
        normalized = _normalize_image_analysis(data)
        return ImageAnalysisResult(**normalized, raw=data)

    async def analyze_parsed_page(
        self,
        url: str,
        title: str,
        h1: str,
        text_excerpt: str,
        context: AnalysisContext,
    ) -> AnalysisResult:
        system = """
Ты — senior-аналитик конкурентной разведки и UX-маркетинга.
Ты анализируешь сайт конкурента по извлеченному контенту страницы.
Верни строго JSON без markdown. Ответ на русском языке.
Важно:
- Анализируй именно сайт/компанию из блока "Анализируемый сайт/компания".
- "Мой бренд" из контекста используй только как точку сравнения.
Схема:
{
  "summary": "краткий вывод по сайту",
  "strengths": ["3-5 пунктов"],
  "weaknesses": ["3-5 пунктов"],
  "unique_offers": ["3-5 пунктов"],
  "recommendations": ["3-7 пунктов"],
  "scores": {
    "offer_score": 0-10,
    "design_score": 0-10,
    "trust_score": 0-10,
    "content_clarity": 0-10,
    "cta_score": 0-10,
    "automation_focus": 0-10
  },
  "positioning_gap": ["что можно усилить относительно рынка"],
  "action_plan": ["конкретные действия для владельца бренда"]
}
"""
        page_text = (
            f"Анализируемый сайт/компания: {url}\nTitle: {title}\nH1: {h1}\n"
            f"Фрагмент текста сайта:\n{text_excerpt}"
        )
        data = self._chat_json(
            settings.openai_model,
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"{self._context_text(context)}\n\n{page_text}",
                },
            ],
        )
        normalized = _normalize_analysis(data)
        return AnalysisResult(**normalized, raw=data)

    async def compare_competitors(
        self, competitors_payload: str, context: AnalysisContext
    ) -> Dict[str, Any]:
        system = """
Ты — стратег по конкурентному анализу. Сравни мой бренд с конкурентами.
Верни строго JSON без markdown. Ответ на русском языке.
Сделай результат удобным для интерфейса: карточки конкурентов, таблица критериев и рекомендации.
Схема:
{
  "type": "comparison",
  "summary": "общий вывод по рынку и позиции моего бренда",
  "competitor_cards": [
    {
      "name": "название",
      "positioning": "как позиционируется",
      "strengths": ["2-4 пункта"],
      "weaknesses": ["2-4 пункта"],
      "threat_level": "низкий|средний|высокий",
      "what_to_learn": ["2-4 идеи, что можно перенять"]
    }
  ],
  "comparison_table": [
    {
      "criterion": "Оффер",
      "own_brand": "оценка моего бренда словами",
      "competitors": [{"name": "конкурент", "value": "оценка словами"}],
      "recommendation": "что улучшить"
    }
  ],
  "brand_recommendations": ["5-8 рекомендаций для моего бренда"],
  "quick_wins": ["3-5 быстрых улучшений"],
  "strategic_moves": ["3-5 стратегических шагов"],
  "risks": ["2-4 риска"],
  "scores": {
    "offer_score": 0-10,
    "design_score": 0-10,
    "trust_score": 0-10,
    "content_clarity": 0-10,
    "automation_focus": 0-10,
    "animation_potential": 0-10
  }
}
Критерии таблицы: Оффер, Доверие, Дизайн, Ясность контента, Продуктовая упаковка, CTA, Доказательства/кейсы.
"""
        data = self._chat_json(
            settings.openai_report_model,
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        f"{self._context_text(context)}\n\n"
                        f"Конкуренты для сравнения:\n{competitors_payload}"
                    ),
                },
            ],
        )
        data.setdefault("type", "comparison")
        data.setdefault("summary", "Сравнение выполнено.")
        data.setdefault("competitor_cards", [])
        data.setdefault("comparison_table", [])
        data.setdefault("brand_recommendations", [])
        data.setdefault("quick_wins", [])
        data.setdefault("strategic_moves", [])
        data.setdefault("risks", [])
        if not isinstance(data.get("scores"), dict):
            data["scores"] = {}
        return data


ai_service = AIService()
