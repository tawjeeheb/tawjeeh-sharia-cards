# Makefile — Tawjeeh Sharia Cards
# الاستخدام:
#   make validate-card CARD=009
#   make build-card CARD=009
#   make lock-card CARD=009
#   make release-card CARD=009

PYTHON := python3
SCRIPTS := scripts
CARD ?= 009

# ── validate-card: يشغّل C1–C23 فقط ─────────────────────────────────────────
.PHONY: validate-card
validate-card:
	@echo "══════════════════════════════════════════"
	@echo "  فحص الجودة — بطاقة $(CARD)"
	@echo "══════════════════════════════════════════"
	$(PYTHON) $(SCRIPTS)/run_card_pipeline.py --card $(CARD)

# ── build-card: يولّد HTML/PDF ثم يشغّل الجودة ───────────────────────────────
.PHONY: build-card
build-card:
	@echo "══════════════════════════════════════════"
	@echo "  بناء وفحص — بطاقة $(CARD)"
	@echo "══════════════════════════════════════════"
	$(PYTHON) $(SCRIPTS)/run_card_pipeline.py --card $(CARD) --build

# ── lock-card: ينشئ scope lock بعد الاعتماد ──────────────────────────────────
.PHONY: lock-card
lock-card:
	@echo "══════════════════════════════════════════"
	@echo "  إنشاء Scope Lock — بطاقة $(CARD)"
	@echo "══════════════════════════════════════════"
	$(PYTHON) $(SCRIPTS)/run_card_pipeline.py --lock $(CARD)

# ── release-card: لا ينجح إلا بـ PASS 24/24 + PDF + evidence + git نظيف ─────
.PHONY: release-card
release-card:
	@echo "══════════════════════════════════════════"
	@echo "  إصدار نهائي — بطاقة $(CARD)"
	@echo "══════════════════════════════════════════"
	$(PYTHON) $(SCRIPTS)/run_card_pipeline.py --card $(CARD) --release

# ── validate-all: فحص جميع البطاقات ─────────────────────────────────────────
.PHONY: validate-all
validate-all:
	@echo "══════════════════════════════════════════"
	@echo "  فحص جميع البطاقات"
	@echo "══════════════════════════════════════════"
	$(PYTHON) $(SCRIPTS)/run_card_pipeline.py --validate-all

# ── help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "أوامر One-Click Card Pipeline:"
	@echo "  make validate-card CARD=009   — فحص C1–C23"
	@echo "  make build-card    CARD=009   — بناء HTML/PDF + فحص"
	@echo "  make lock-card     CARD=009   — إنشاء Scope Lock"
	@echo "  make release-card  CARD=009   — إصدار نهائي (يتطلب git نظيف)"
	@echo "  make validate-all             — فحص جميع البطاقات"
	@echo ""
