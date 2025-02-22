<template>
  <div class="auth-header">
    <template v-if="isAuthenticated">
      <span class="username">{{ nombre }}</span>
      <el-button type="default" @click="logout">Cerrar Sesión</el-button>
    </template>
    <template v-else>
      <el-button type="default" @click="$router.push('/login')"
        >Iniciar Sesión</el-button
      >
    </template>
  </div>
</template>

<script>
export default {
  name: "AuthHeader",
  data() {
    return {
      nombre: localStorage.getItem("nombre") || "",
    };
  },
  computed: {
    isAuthenticated() {
      return !!localStorage.getItem("token");
    },
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      localStorage.removeItem("nombre");
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.auth-header {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  color: #606266;
}
</style>
