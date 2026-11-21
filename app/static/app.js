const app = document.querySelector("#app");
const state = {
  questions: null,
  step: 0,
  symptoms: new Set(),
  dangerSigns: new Set(),
  symptomOnsetDays: new Map(),
  environment: "",
  season: "",
};

const steps = [
  {
    title: "Apakah ada tanda bahaya?",
    description: "Pilih semua yang sedang dialami. Jika ada, aplikasi akan langsung menampilkan peringatan.",
  },
  {
    title: "Gejala apa yang dialami?",
    description: "Pilih satu atau beberapa gejala yang tersedia di dalam ontologi.",
  },
  {
    title: "Faktor lingkungan",
    description: "Opsional. Pilih faktor paparan dan musim jika diketahui; informasi ini hanya membantu mengurutkan kecocokan.",
  },
  {
    title: "Periksa jawaban Anda",
    description: "Tinjau pilihan sebelum melihat informasi yang terkait di dalam ontologi.",
  },
];

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function selectedLabels(options, selected) {
  return options.filter((option) => selected.has(option.id)).map((option) => option.label);
}

function makeOption(option, selected, onChange) {
  const label = makeElement("label", "option");
  const input = document.createElement("input");
  input.type = "checkbox";
  input.value = option.id;
  input.checked = selected.has(option.id);
  input.addEventListener("change", () => onChange(option.id, input.checked));
  label.append(input, makeElement("span", "", option.label));
  return label;
}

function renderOptions(container, options, selected, onChange) {
  for (const option of options) container.append(makeOption(option, selected, onChange));
}

function render() {
  app.replaceChildren();
  const { title, description } = steps[state.step];
  const header = makeElement("div", "progress-row");
  header.append(
    makeElement("span", "", "LANGKAH " + (state.step + 1) + " DARI " + steps.length),
    makeElement("span", "", Math.round(((state.step + 1) / steps.length) * 100) + "%"),
  );
  const track = makeElement("div", "progress-track");
  const fill = makeElement("div", "progress-fill");
  fill.style.width = ((state.step + 1) / steps.length) * 100 + "%";
  track.append(fill);
  app.append(header, track, makeElement("h2", "", title), makeElement("p", "step-description", description));

  if (state.step === 0) renderDangerStep();
  if (state.step === 1) renderSymptomsStep();
  if (state.step === 2) renderExposureStep();
  if (state.step === 3) renderReviewStep();
  renderNavigation();
}

function renderDangerStep() {
  const list = makeElement("div", "option-list");
  renderOptions(list, state.questions.danger_signs, state.dangerSigns, (id, checked) => {
    if (checked) state.dangerSigns.add(id);
    else state.dangerSigns.delete(id);
    render();
  });
  app.append(list);
  if (state.dangerSigns.size) {
    const alert = makeElement("div", "inline-alert");
    alert.setAttribute("role", "alert");
    alert.append(
      makeElement("strong", "", "Tanda bahaya dipilih"),
      makeElement("p", "", "Segera cari pertolongan medis. Jangan menunggu proses tanya jawab selesai."),
    );
    app.append(alert);
  }
}

function renderSymptomsStep() {
  const list = makeElement("div", "option-list");
  const onsetFields = makeElement("div", "onset-list");
  const noSymptomsHint = makeElement(
    "p",
    "timing-note",
    "Tidak menemukan gejala yang sesuai? Anda dapat melanjutkan tanpa memilih gejala; hasil akan menjelaskan keterbatasan basis pengetahuan.",
  );
  noSymptomsHint.hidden = state.symptoms.size > 0;
  renderOptions(list, state.questions.symptoms, state.symptoms, (id, checked) => {
    if (checked) {
      state.symptoms.add(id);
    } else {
      state.symptoms.delete(id);
      state.symptomOnsetDays.delete(id);
    }
    noSymptomsHint.hidden = state.symptoms.size > 0;
    renderOnsetFields(onsetFields);
  });
  app.append(list, noSymptomsHint);
  if (state.questions.onset_timing_available) {
    const timingNote = makeElement(
      "p",
      "timing-note",
      "Jika tahu, isi hari ke berapa tiap gejala mulai dirasakan. Ontologi mencatat waktu mulai per gejala, bukan durasi total penyakit. Isian ini hanya ditampilkan sebagai konteks dan tidak memengaruhi urutan hasil.",
    );
    timingNote.id = "onset-note";
    app.append(timingNote);
    app.append(onsetFields);
    renderOnsetFields(onsetFields);
  }
}

function renderOnsetFields(container) {
  container.replaceChildren();
  for (const symptom of state.questions.symptoms) {
    if (!state.symptoms.has(symptom.id)) continue;
    const wrapper = makeElement("div", "onset-field");
    const input = document.createElement("input");
    input.type = "number";
    input.min = "1";
    input.step = "1";
    input.inputMode = "numeric";
    input.id = "onset-" + symptom.id;
    input.value = state.symptomOnsetDays.get(symptom.id) || "";
    input.setAttribute("aria-describedby", "onset-note");
    const label = makeElement(
      "label",
      "",
      symptom.label + " — hari ke berapa mulai dirasakan? (opsional)",
    );
    label.htmlFor = input.id;
    input.addEventListener("input", () => {
      if (input.value === "") {
        state.symptomOnsetDays.delete(symptom.id);
      } else {
        state.symptomOnsetDays.set(symptom.id, input.value);
      }
    });
    wrapper.append(label, input);
    container.append(wrapper);
  }
}

function makeSelect(labelText, options, selectedId, update) {
  const wrapper = makeElement("div", "select-field");
  const label = makeElement("label", "", labelText);
  const select = document.createElement("select");
  const placeholder = makeElement("option", "", "Tidak dipilih");
  placeholder.value = "";
  select.append(placeholder);
  for (const option of options) {
    const choice = makeElement("option", "", option.label);
    choice.value = option.id;
    select.append(choice);
  }
  select.value = selectedId;
  select.addEventListener("change", () => update(select.value));
  label.append(select);
  wrapper.append(label);
  return wrapper;
}

function renderExposureStep() {
  const grid = makeElement("div", "select-grid");
  grid.append(
    makeSelect("Faktor lingkungan", state.questions.environments, state.environment, (value) => {
      state.environment = value;
    }),
    makeSelect("Musim", state.questions.seasons, state.season, (value) => {
      state.season = value;
    }),
  );
  app.append(grid);
}

function reviewRow(title, values, editStep) {
  const row = makeElement("div", "review-row");
  row.append(makeElement("strong", "", title));
  const content = values.length ? values.join(", ") : "Tidak dipilih";
  row.append(makeElement("p", "", content));
  const edit = makeElement("button", "review-edit", "Ubah");
  edit.type = "button";
  edit.addEventListener("click", () => {
    state.step = editStep;
    render();
  });
  row.append(edit);
  return row;
}

function renderReviewStep() {
  const rows = makeElement("div", "review-list");
  const symptomAnswers = state.questions.symptoms
    .filter((symptom) => state.symptoms.has(symptom.id))
    .map((symptom) => {
      const onsetDay = state.symptomOnsetDays.get(symptom.id);
      return onsetDay
        ? symptom.label + " (hari ke-" + onsetDay + ")"
        : symptom.label;
    });
  rows.append(
    reviewRow("Tanda bahaya", selectedLabels(state.questions.danger_signs, state.dangerSigns), 0),
    reviewRow("Gejala dan hari mulai (jika diisi)", symptomAnswers, 1),
    reviewRow(
      "Faktor lingkungan dan musim",
      [
        ...selectedLabels(state.questions.environments.filter((item) => item.id === state.environment), new Set([state.environment])),
        ...selectedLabels(state.questions.seasons.filter((item) => item.id === state.season), new Set([state.season])),
      ],
      2,
    ),
  );
  app.append(rows);
}

function section(card, title, values, format = (value) => value.label) {
  if (!values || values.length === 0) return;
  const wrapper = makeElement("div", "result-section");
  wrapper.append(makeElement("strong", "", title));
  wrapper.append(makeElement("p", "", values.map(format).join(", ")));
  card.append(wrapper);
}

function renderResults(data) {
  app.replaceChildren();
  app.append(makeElement("p", "eyebrow", "RINGKASAN INFORMASI"));
  app.append(makeElement("h2", "", "Hasil dari basis pengetahuan"));
  app.append(makeElement("p", "step-description", data.message));

  if (data.emergency) {
    const alert = makeElement("div", "result-alert");
    alert.setAttribute("role", "alert");
    alert.append(
      makeElement("strong", "", "Segera cari pertolongan medis"),
      makeElement("p", "", "Tanda bahaya yang dipilih tercatat dalam ontologi. Jangan menunda pertolongan untuk meninjau daftar kecocokan."),
    );
    app.append(alert);
  }

  app.append(makeElement("p", "method-note", data.matching_method));
  if (!data.results.length) {
    app.append(makeElement("p", "step-description", data.emergency ? "Tidak ada kecocokan gejala untuk ditampilkan." : "Basis pengetahuan tidak menemukan kecocokan untuk pilihan ini."));
  }

  for (const result of data.results) {
    const card = makeElement("article", "result-card");
    card.append(makeElement("h3", "", result.label));
    card.append(makeElement("p", "result-meta", result.matched_symptom_count + " gejala terpilih tercatat pada relasi penyakit ini"));
    section(card, "Gejala yang cocok", result.matched_symptoms, (value) => {
      const timing = [];
      if (value.onset_day !== null) timing.push("ontologi: hari ke-" + value.onset_day);
      if (value.reported_onset_day !== null) {
        timing.push("jawaban Anda: hari ke-" + value.reported_onset_day);
      }
      return timing.length ? value.label + " (" + timing.join("; ") + ")" : value.label;
    });
    section(card, "Faktor lingkungan terkait", result.environments);
    section(card, "Musim terkait", result.seasons);
    section(card, "Tanda bahaya terkait", result.danger_signs);
    section(card, "Penanganan mandiri yang tercatat", result.self_care);
    section(card, "Rujukan medis yang tercatat", result.medical_referrals);
    section(card, "Tindakan yang dihindari menurut ontologi", result.avoid);
    section(card, "Sumber dalam ontologi", result.references, (value) => value);
    app.append(card);
  }

  const reset = makeElement("div", "reset-row");
  const button = makeElement("button", "button-primary", "Mulai lagi");
  button.type = "button";
  button.addEventListener("click", () => {
    state.step = 0;
    state.symptoms.clear();
    state.dangerSigns.clear();
    state.symptomOnsetDays.clear();
    state.environment = "";
    state.season = "";
    render();
  });
  reset.append(button);
  app.append(reset);
}

function renderNavigation() {
  const nav = makeElement("div", "navigation");
  const back = makeElement("button", "button-secondary", "Kembali");
  back.type = "button";
  back.disabled = state.step === 0;
  back.addEventListener("click", () => {
    state.step = Math.max(0, state.step - 1);
    render();
  });
  const next = makeElement("button", "button-primary", state.step === 3 ? "Lihat informasi" : "Lanjut");
  next.type = "button";
  next.addEventListener("click", async () => {
    if (state.step === 1) {
      const invalidOnset = [...state.symptomOnsetDays.values()].some(
        (value) => !/^\d+$/.test(value) || Number(value) < 1,
      );
      if (invalidOnset) {
        showError("Hari mulai gejala harus berupa bilangan bulat minimal 1.");
        return;
      }
    }
    if (state.step < 3) {
      state.step += 1;
      render();
      return;
    }
    next.disabled = true;
    next.textContent = "Memeriksa...";
    try {
      const response = await fetch("/api/consultations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptoms: [...state.symptoms],
          danger_signs: [...state.dangerSigns],
          symptom_onset_days: Object.fromEntries(
            [...state.symptomOnsetDays.entries()].map(([id, value]) => [id, Number(value)]),
          ),
          environment: state.environment || null,
          season: state.season || null,
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Permintaan tidak dapat diproses.");
      renderResults(data);
    } catch (error) {
      showError(error.message || "Terjadi kesalahan saat menghubungi layanan.");
    }
  });
  nav.append(back, next);
  app.append(nav);
}

function showError(message) {
  const existing = app.querySelector(".form-error");
  if (existing) existing.remove();
  const error = makeElement("p", "error-message form-error", message);
  error.setAttribute("role", "alert");
  app.insertBefore(error, app.querySelector(".navigation"));
}

async function initialize() {
  try {
    const response = await fetch("/api/questions");
    if (!response.ok) throw new Error("Pertanyaan dari basis pengetahuan tidak dapat dimuat.");
    state.questions = await response.json();
    render();
  } catch (error) {
    app.replaceChildren();
    const message = makeElement("p", "error-message", error.message);
    message.setAttribute("role", "alert");
    app.append(message);
  }
}

initialize();
