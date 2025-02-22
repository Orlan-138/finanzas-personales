<template>
  <div v-if="$route.path === '/login'">
    <router-view />
  </div>
  <el-container v-else class="app-container">
    <el-aside width="200px">
      <el-menu router default-active="/">
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/transacciones">
          <el-icon><Document /></el-icon>
          <span>Transacciones</span>
        </el-menu-item>
        <el-menu-item index="/inversiones">
          <el-icon><TrendCharts /></el-icon>
          <span>Inversiones</span>
        </el-menu-item>
        <el-menu-item index="/creditos">
          <el-icon><Money /></el-icon>
          <span>Créditos</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="main-container">
      <el-header height="60px">
        <auth-header />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script>
import {
  HomeFilled,
  Document,
  TrendCharts,
  Money,
} from "@element-plus/icons-vue";
import AuthHeader from "./components/common/AuthHeader.vue";

export default {
  name: "App",
  components: {
    HomeFilled,
    Document,
    TrendCharts,
    Money,
    AuthHeader,
  },
  data() {
    return {
      resizeObserverError: null,
    };
  },
  mounted() {
    // Solución para el error de ResizeObserver
    this.resizeObserverError = (error) => {
      if (error.message.includes("ResizeObserver")) {
        const resizeObserverErr = document.getElementById(
          "webpack-dev-server-client-overlay"
        );
        if (resizeObserverErr) {
          resizeObserverErr.style.display = "none";
        }
      }
    };
    window.addEventListener("error", this.resizeObserverError);
  },
  beforeUnmount() {
    // Limpiar el event listener cuando el componente se desmonta
    if (this.resizeObserverError) {
      window.removeEventListener("error", this.resizeObserverError);
    }
  },
};
</script>

<style>
.app-container {
  height: 100vh;
  overflow: hidden;
}

.main-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

#app {
  height: 100vh;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #f5f7fa;
}

.el-header {
  position: relative;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
}

.el-main {
  overflow-y: auto;
  padding: 20px;
}
</style>
