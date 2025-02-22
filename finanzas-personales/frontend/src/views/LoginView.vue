<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>Iniciar Sesión</h2>
      </template>
      <el-form :model="loginForm" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="loginForm.username"
            placeholder="Email"
            type="email"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="loginForm.password"
            placeholder="Contraseña"
            type="password"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" style="width: 100%">
            Iniciar Sesión
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import api from "@/services/api";
import { ElMessage } from "element-plus";

export default {
  name: "LoginView",
  data() {
    return {
      loginForm: {
        username: "",
        password: "",
      },
    };
  },
  methods: {
    async handleLogin() {
      try {
        console.log("Intentando login con:", this.loginForm);

        // Crear URLSearchParams en lugar de FormData
        const params = new URLSearchParams();
        params.append("username", this.loginForm.username);
        params.append("password", this.loginForm.password);

        const response = await api.post("/token", params, {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        console.log("Respuesta login:", response.data);
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("username", this.loginForm.username);
        localStorage.setItem("nombre", response.data.nombre);
        ElMessage.success("Inicio de sesión exitoso");
        this.$router.push("/");
      } catch (error) {
        console.error("Error detallado:", error);
        ElMessage.error(
          `Error al iniciar sesión: ${
            error.response?.data?.detail || error.message
          }`
        );
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}
.login-card {
  width: 400px;
}
</style>
