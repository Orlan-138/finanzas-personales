<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Balance General</span>
            </div>
          </template>
          <div class="balance-info">
            <p>Balance: {{ formatCurrency(resumen?.balance_neto || 0) }}</p>
            <p>
              Patrimonio: {{ formatCurrency(resumen?.patrimonio_neto || 0) }}
            </p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "DashboardView",
  data() {
    return {
      resumen: null,
    };
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat("es-ES", {
        style: "currency",
        currency: "EUR",
      }).format(value);
    },
    async obtenerResumen() {
      try {
        const response = await api.get("/transacciones/resumen/");
        this.resumen = response.data;
      } catch (error) {
        console.error("Error al obtener resumen:", error);
      }
    },
  },
  mounted() {
    this.obtenerResumen();
  },
};
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.balance-info {
  font-size: 1.2em;
}
</style>
