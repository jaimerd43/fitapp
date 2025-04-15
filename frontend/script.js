document.addEventListener("DOMContentLoaded", () => {
  const authBox = document.getElementById("auth");
  const appBox = document.getElementById("app");
  const preview = document.getElementById("preview");
  const cargando = document.getElementById("cargando");
  const resultado = document.getElementById("resultado");

  const token = localStorage.getItem("token");
  if (token) {
    authBox.classList.add("hidden");
    appBox.classList.remove("hidden");
  }

  document.getElementById("foto").addEventListener("change", () => {
    const file = document.getElementById("foto").files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      preview.src = e.target.result;
      preview.classList.remove("hidden");
    };
    reader.readAsDataURL(file);
  });

  window.login = async function () {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const res = await fetch("/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (res.ok) {
      const data = await res.json();
      localStorage.setItem("token", data.access_token);
      authBox.classList.add("hidden");
      appBox.classList.remove("hidden");
    } else {
      alert("Credenciales incorrectas");
    }
  }

  window.registrar = async function () {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const res = await fetch("/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (res.ok) {
      alert("Usuario creado. Ahora puedes iniciar sesión.");
    } else {
      alert("Ya existe una cuenta con este correo.");
    }
  }

  window.enviarFoto = async function () {
    const file = document.getElementById("foto").files[0];
    if (!file) return alert("Primero selecciona una foto");

    const formData = new FormData();
    formData.append("foto", file);

    cargando.classList.remove("hidden");
    resultado.textContent = "";

    const res = await fetch("/procesar-foto", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token")
      },
      body: formData
    });

    const data = await res.json();
    cargando.classList.add("hidden");

    if (res.ok) {
      resultado.textContent = data.resultado;
    } else {
      resultado.textContent = data.detail || "Error al procesar";
    }
  }
});
