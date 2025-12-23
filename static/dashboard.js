const PACK_ID = "pack_demo_5docs";
const token = localStorage.getItem("token");

if (!token) {
  window.location.href = "/login.html";
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/login.html";
}

/* GENERAR PACK */
document.getElementById("generateBtn").onclick = () => {

  const data = {
    NOMBRE: document.getElementById("NOMBRE").value.trim(),
    DNI: document.getElementById("DNI").value.trim(),
    DIRECCION: document.getElementById("DIRECCION").value.trim(),
    LOCALIDAD: document.getElementById("LOCALIDAD").value.trim(),
    EXPEDIENTE: document.getElementById("EXPEDIENTE").value.trim()
  };

  for (const k in data) {
    if (!data[k]) {
      alert("Completá todos los campos");
      return;
    }
  }

  const btn = document.getElementById("generateBtn");
  const status = document.getElementById("statusMsg");

  btn.disabled = true;
  status.textContent = "Generando documentación...";

  fetch("/client/generate-pack", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + token
    },
    body: JSON.stringify({
      pack_id: PACK_ID,
      data: data
    })
  })
  .then(r => r.json())
  .then(res => {
    btn.disabled = false;

    if (!res.ok) {
      status.textContent = "Error generando documentación";
      status.className = "status error";
      return;
    }

    status.innerHTML =
      `✔ Generado correctamente –
       <a href="${res.zip_download}" target="_blank">Descargar ZIP</a>`;
    status.className = "status ok";

    loadHistory();
  })
  .catch(() => {
    btn.disabled = false;
    status.textContent = "Error inesperado";
    status.className = "status error";
  });
};

/* HISTORIAL */
function loadHistory() {
  fetch("/client/packs", {
    headers: { Authorization: "Bearer " + token }
  })
  .then(r => r.json())
  .then(res => {
    const table = document.getElementById("historyTable");
    table.innerHTML = "";

    res.packs.forEach(p => {
      table.innerHTML += `
        <tr>
          <td>${p.pack_id}</td>
          <td>${p.created_at}</td>
          <td>${p.email_sent ? "Enviado" : "Error"}</td>
          <td><a href="/download/${p.zip_name}" target="_blank">ZIP</a></td>
        </tr>`;
    });
  });
}

loadHistory();
