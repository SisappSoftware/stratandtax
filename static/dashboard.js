const token = localStorage.getItem("token");
const PACK_ID = "pack_demo_5docs";

if (!token) {
  window.location.href = "/login.html";
}

const form = document.getElementById("dynamicForm");
const statusMsg = document.getElementById("statusMsg");
const generateBtn = document.getElementById("generateBtn");
const packsTable = document.getElementById("packsTable");

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/login.html";
}

/* ===== USER ===== */
fetch("/auth/me", {
  headers: { Authorization: `Bearer ${token}` }
})
.then(r => r.json())
.then(u => {
  document.getElementById("userEmail").textContent = u.email;
});

fetch("/client/active-form", {
  headers: { Authorization: `Bearer ${token}` }
})
.then(r => r.json())
.then(res => {
  if (!res.ok) {
    statusMsg.textContent = "Error cargando formulario";
    return;
  }

  // LIMPIAMOS POR LAS DUDAS
  form.innerHTML = "";

  res.schema.fields.forEach(field => {
    const div = document.createElement("div");
    div.className = "field";

    const label = document.createElement("label");
    label.textContent = field.label;

    const input = document.createElement("input");
    input.name = field.key;
    input.placeholder = field.label;
    input.required = true;

    div.appendChild(label);
    div.appendChild(input);
    form.appendChild(div);
  });
});

/* ===== GENERATE ===== */
generateBtn.onclick = () => {
  const inputs = document.querySelectorAll("#dynamicForm input");
  const data = {};

  for (const input of inputs) {
    if (!input.value.trim()) {
      alert("Completá todos los campos");
      input.focus();
      return;
    }
    data[input.name] = input.value;
  }

  statusMsg.textContent = "Generando documentación...";
  generateBtn.disabled = true;

  fetch("/client/generate-pack", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      pack_id: PACK_ID,
      data: data
    })
  })
  .then(r => r.json())
  .then(res => {
    generateBtn.disabled = false;

    if (!res.ok) {
      statusMsg.textContent = "Error generando documentación";
      return;
    }

    statusMsg.textContent =
      "✔ Documentación generada y enviada por email";

    form.reset();
    loadHistory();
  });
};


/* ===== HISTORY ===== */
function loadHistory() {
  fetch("/client/packs", {
    headers: { Authorization: `Bearer ${token}` }
  })
  .then(r => r.json())
  .then(res => {
    packsTable.innerHTML = "";
    res.packs.forEach(p => {
      packsTable.innerHTML += `
        <tr>
          <td>${p.pack_id}</td>
          <td>${p.created_at}</td>
          <td>${p.email_sent ? "Enviado" : "Error"}</td>
          <td><a href="/download/${p.zip_name}" target="_blank">Descargar</a></td>
        </tr>
      `;
    });
  });
}

loadHistory();
