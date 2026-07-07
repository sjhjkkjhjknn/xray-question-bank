(function () {
  const bank = window.QUESTION_BANK;
  const questions = bank.questions;
  const storageKey = "xray-question-bank:v1";

  const state = {
    mode: "all",
    section: "all",
    type: "all",
    index: 0,
    order: [],
    selected: new Set(),
    revealed: false,
    autoAdvanceTimer: null,
    records: loadRecords(),
  };

  const els = {
    progressText: document.getElementById("progressText"),
    totalCount: document.getElementById("totalCount"),
    doneCount: document.getElementById("doneCount"),
    wrongCount: document.getElementById("wrongCount"),
    accuracyText: document.getElementById("accuracyText"),
    resetBtn: document.getElementById("resetBtn"),
    sectionSelect: document.getElementById("sectionSelect"),
    typeSelect: document.getElementById("typeSelect"),
    questionTag: document.getElementById("questionTag"),
    questionType: document.getElementById("questionType"),
    questionImage: document.getElementById("questionImage"),
    optionGrid: document.getElementById("optionGrid"),
    answerState: document.getElementById("answerState"),
    prevBtn: document.getElementById("prevBtn"),
    nextBtn: document.getElementById("nextBtn"),
    modeButtons: Array.from(document.querySelectorAll(".mode-button")),
  };

  function loadRecords() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return { answered: {}, wrong: {}, totalSubmits: 0, totalCorrect: 0 };
      const parsed = JSON.parse(raw);
      return {
        answered: parsed.answered || {},
        wrong: parsed.wrong || {},
        totalSubmits: parsed.totalSubmits || 0,
        totalCorrect: parsed.totalCorrect || 0,
      };
    } catch {
      return { answered: {}, wrong: {}, totalSubmits: 0, totalCorrect: 0 };
    }
  }

  function saveRecords() {
    localStorage.setItem(storageKey, JSON.stringify(state.records));
  }

  function shuffle(items) {
    const copy = items.slice();
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function currentPool() {
    let pool = questions.filter((question) => {
      const sectionOk = state.section === "all" || question.sectionKey === state.section;
      const typeOk = state.type === "all" || question.type === state.type;
      const wrongOk = state.mode !== "wrong" || Boolean(state.records.wrong[question.id]);
      return sectionOk && typeOk && wrongOk;
    });
    if (state.mode === "random") pool = shuffle(pool);
    return pool;
  }

  function rebuildOrder(keepId) {
    state.order = currentPool().map((question) => question.id);
    if (keepId && state.order.includes(keepId)) {
      state.index = state.order.indexOf(keepId);
    } else {
      state.index = Math.min(state.index, Math.max(0, state.order.length - 1));
    }
    state.selected = new Set();
    state.revealed = false;
    clearAutoAdvance();
  }

  function questionById(id) {
    return questions.find((question) => question.id === id);
  }

  function currentQuestion() {
    return questionById(state.order[state.index]);
  }

  function sameAnswer(left, right) {
    const a = left.slice().sort().join(",");
    const b = right.slice().sort().join(",");
    return a === b;
  }

  function renderStats() {
    const done = Object.keys(state.records.answered).length;
    const wrong = Object.keys(state.records.wrong).length;
    const accuracy = state.records.totalSubmits
      ? Math.round((state.records.totalCorrect / state.records.totalSubmits) * 100)
      : 0;
    els.totalCount.textContent = String(questions.length);
    els.doneCount.textContent = String(done);
    els.wrongCount.textContent = String(wrong);
    els.accuracyText.textContent = `${accuracy}%`;
  }

  function renderQuestion() {
    const question = currentQuestion();
    renderStats();
    els.prevBtn.disabled = state.index <= 0;
    els.nextBtn.disabled = state.index >= state.order.length - 1;

    if (!question) {
      els.progressText.textContent = "当前筛选无题目";
      els.questionTag.textContent = "无题目";
      els.questionType.textContent = "";
      els.questionImage.removeAttribute("src");
      els.optionGrid.innerHTML = "";
      els.answerState.textContent = "调整章节或题型后继续。";
      els.answerState.className = "answer-state";
      return;
    }

    els.progressText.textContent = `${state.index + 1} / ${state.order.length}`;
    els.questionTag.textContent = `${question.section} 第 ${question.number} 题`;
    els.questionType.textContent = question.type === "multiple" ? "多选题" : "单选题";
    els.questionImage.src = question.image;
    els.optionGrid.innerHTML = "";

    question.options.forEach((option) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "option-button";
      button.textContent = option;
      if (state.selected.has(option)) button.classList.add("selected");
      if (state.revealed && question.answer.includes(option)) button.classList.add("correct");
      if (state.revealed && state.selected.has(option) && !question.answer.includes(option)) button.classList.add("wrong");
      button.addEventListener("click", () => toggleOption(option, question));
      els.optionGrid.appendChild(button);
    });

    if (!state.revealed) {
      els.answerState.textContent = "";
      els.answerState.className = "answer-state";
    }
  }

  function toggleOption(option, question) {
    if (state.revealed) return;
    if (question.type === "single") {
      state.selected = new Set([option]);
      submitAnswer();
      return;
    } else if (state.selected.has(option)) {
      state.selected.delete(option);
    } else {
      state.selected.add(option);
    }
    if (state.selected.size >= question.answer.length) {
      submitAnswer();
    } else {
      renderQuestion();
    }
  }

  function submitAnswer() {
    const question = currentQuestion();
    if (!question || state.selected.size === 0) return;
    clearAutoAdvance();
    const chosen = Array.from(state.selected);
    const correct = sameAnswer(chosen, question.answer);
    state.revealed = true;
    state.records.totalSubmits += 1;
    if (correct) state.records.totalCorrect += 1;
    state.records.answered[question.id] = {
      last: chosen,
      correct,
      time: new Date().toISOString(),
    };
    if (correct) {
      delete state.records.wrong[question.id];
    } else {
      state.records.wrong[question.id] = {
        last: chosen,
        answer: question.answer,
        time: new Date().toISOString(),
      };
    }
    saveRecords();
    renderQuestion();
    els.answerState.textContent = correct
      ? `正确：${question.answer.join("、")}`
      : `错误，正确答案：${question.answer.join("、")}`;
    els.answerState.className = `answer-state ${correct ? "ok" : "bad"}`;
    if (correct && state.index < state.order.length - 1) {
      state.autoAdvanceTimer = window.setTimeout(() => goto(1), 550);
    }
  }

  function goto(delta) {
    clearAutoAdvance();
    state.index = Math.max(0, Math.min(state.order.length - 1, state.index + delta));
    state.selected = new Set();
    state.revealed = false;
    renderQuestion();
  }

  function clearAutoAdvance() {
    if (!state.autoAdvanceTimer) return;
    window.clearTimeout(state.autoAdvanceTimer);
    state.autoAdvanceTimer = null;
  }

  function initFilters() {
    bank.meta.sections.forEach((section) => {
      const option = document.createElement("option");
      option.value = section.key;
      option.textContent = section.name;
      els.sectionSelect.appendChild(option);
    });
  }

  function bindEvents() {
    els.modeButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const current = currentQuestion();
        state.mode = button.dataset.mode;
        els.modeButtons.forEach((item) => item.classList.toggle("active", item === button));
        rebuildOrder(current && current.id);
        renderQuestion();
      });
    });
    els.sectionSelect.addEventListener("change", () => {
      state.section = els.sectionSelect.value;
      rebuildOrder();
      renderQuestion();
    });
    els.typeSelect.addEventListener("change", () => {
      state.type = els.typeSelect.value;
      rebuildOrder();
      renderQuestion();
    });
    els.prevBtn.addEventListener("click", () => goto(-1));
    els.nextBtn.addEventListener("click", () => goto(1));
    els.resetBtn.addEventListener("click", () => {
      if (!confirm("清空本机答题记录和错题库？")) return;
      state.records = { answered: {}, wrong: {}, totalSubmits: 0, totalCorrect: 0 };
      saveRecords();
      rebuildOrder();
      renderQuestion();
    });
  }

  function registerServiceWorker() {
    if (!("serviceWorker" in navigator)) return;
    if (!location.protocol.startsWith("http")) return;
    navigator.serviceWorker.register("sw.js").catch(() => {});
  }

  initFilters();
  bindEvents();
  rebuildOrder();
  renderQuestion();
  registerServiceWorker();
})();
