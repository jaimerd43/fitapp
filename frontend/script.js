document.addEventListener("DOMContentLoaded", () => {
  const authBox = document.getElementById("auth");
  const appBox = document.getElementById("app");
  const preview = document.getElementById("preview");
  const uploadPlaceholder = document.getElementById("upload-placeholder");
  const cargando = document.getElementById("cargando");
  const resultContainer = document.getElementById("result-container");
  const resultado = document.getElementById("resultado");
  const chatBox = document.getElementById("chat-box");
  const conversacion = document.getElementById("conversacion");
  const ajusteInput = document.getElementById("ajuste-input");
  
  // Variable global para rastrear si se hicieron ajustes
  window.seHicieronAjustes = false;
  
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
      uploadPlaceholder.classList.add("hidden");
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
  };
  
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
  };
  
  window.enviarFoto = async function () {
    const file = document.getElementById("foto").files[0];
    if (!file) return alert("Primero selecciona una foto");
    
    const formData = new FormData();
    formData.append("foto", file);
    
    cargando.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    resultado.textContent = "";
    
    // Reset ajustes tracking when sending a new photo
    window.seHicieronAjustes = false;
    
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
      resultContainer.classList.remove("hidden");
      chatBox.classList.remove("hidden");
      conversacion.innerHTML = ""; // Reiniciar chat para nueva comida
    } else {
      resultado.textContent = data.detail || "Error al procesar";
    }
  };
  
  window.enviarAjuste = async function () {
    const mensaje = ajusteInput.value.trim();
    if (!mensaje) return;
    
    // Marcar que se hicieron ajustes
    window.seHicieronAjustes = true;
    
    // Mostrar mensaje del usuario con estilo
    const userBubble = document.createElement("div");
    userBubble.textContent = mensaje;
    userBubble.className = "bubble-user px-4 py-3 text-white max-w-xs self-end";
    conversacion.appendChild(userBubble);
    
    ajusteInput.value = "";
    
    // Llamar al backend
    const res = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + localStorage.getItem("token")
      },
      body: JSON.stringify({ mensaje })
    });
    
    const data = await res.json();
    
    // Mostrar respuesta del bot con estilo
    const botBubble = document.createElement("div");
    botBubble.textContent = data.respuesta;
    botBubble.className = "bubble-bot px-4 py-3 text-gray-200 max-w-xs self-start";
    conversacion.appendChild(botBubble);
    
    conversacion.scrollTop = conversacion.scrollHeight;
  };
  
  window.guardarResultadoFinal = async function () {
    const res = await fetch("/guardar-ajuste-final", {
      method: "POST",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token")
      }
    });
    
    const data = await res.json();
    
    // Mostrar mensaje según si hubo ajustes o no
    if (window.seHicieronAjustes) {
      alert("Análisis ajustado guardado correctamente ✅");
    } else {
      alert("Análisis inicial guardado correctamente ✅");
    }
    
    // Limpiar la conversación y ocultar el chat box
    conversacion.innerHTML = "";
    ajusteInput.value = "";
    chatBox.classList.add("hidden");
    
    // Reiniciar la bandera de ajustes
    window.seHicieronAjustes = false;
  };
  
  // Añadir acción de Enter para los campos de texto
  document.getElementById("ajuste-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      window.enviarAjuste();
    }
  });
  
  document.getElementById("password").addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      window.login();
    }
  });
});