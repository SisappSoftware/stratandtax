fetch("/superadmin/packs", {
  headers: { Authorization: "Bearer " + token }
})
.then(r => r.json())
.then(data => {
  const container = document.getElementById("packsList");
  container.innerHTML = "";

  data.packs.forEach(pack => {
    const div = document.createElement("div");
    div.className = "pack-card";
    div.innerHTML = `
      <h3>${pack.id}</h3>
      <ul>
        ${pack.docs.map(d =>
          `<li>
            ${d}
            <a href="/superadmin/templates/${pack.id}/${d}">Descargar</a>
          </li>`).join("")}
      </ul>
    `;
    container.appendChild(div);
  });
});
