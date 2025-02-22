<template>
  <div class="transacciones">
    <h1>Transacciones</h1>

    <!-- Botón para nueva transacción -->
    <el-button
      type="primary"
      @click="dialogVisible = true"
      style="margin-bottom: 20px"
    >
      Nueva Transacción
    </el-button>

    <!-- Tabla de transacciones -->
    <el-table :data="transaccionesFiltradas" style="width: 100%">
      <el-table-column prop="fecha" label="Fecha" width="120">
        <template #default="{ row }">
          {{ formatDate(row.fecha) }}
        </template>
      </el-table-column>
      <el-table-column prop="tipo" label="Tipo" width="150">
        <template #default="{ row }">
          {{ formatTipo(row.tipo) }}
        </template>
      </el-table-column>
      <el-table-column prop="descripcion" label="Descripción" />
      <el-table-column prop="categoria" label="Categoría" width="150">
        <template #default="{ row }">
          {{ formatCategoria(row.categoria) }}
        </template>
      </el-table-column>
      <el-table-column prop="monto" label="Monto" width="120">
        <template #default="{ row }">
          {{ formatCurrency(row.monto) }}
        </template>
      </el-table-column>
      <el-table-column label="Acciones" width="120">
        <template #default="{ row }">
          <el-button
            type="primary"
            size="small"
            @click="editarTransaccion(row)"
          >
            Editar
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Diálogo para crear/editar -->
    <el-dialog
      v-model="dialogVisible"
      :title="modoEdicion ? 'Editar Transacción' : 'Nueva Transacción'"
    >
      <el-form :model="transaccionForm" label-width="120px">
        <el-form-item label="Tipo">
          <el-select
            v-model="transaccionForm.tipo"
            placeholder="Seleccione tipo"
          >
            <el-option label="Ingreso" value="ingreso" />
            <el-option label="Gasto" value="gasto" />
            <el-option
              label="Transferencia Recibida"
              value="transferencia_recibida"
            />
            <el-option
              label="Transferencia Emitida"
              value="transferencia_emitida"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Monto">
          <el-input-number
            v-model="transaccionForm.monto"
            :precision="2"
            :step="0.01"
          />
        </el-form-item>
        <el-form-item label="Fecha">
          <el-date-picker
            v-model="transaccionForm.fecha"
            type="date"
            placeholder="Seleccione fecha"
          />
        </el-form-item>
        <el-form-item label="Descripción">
          <el-input v-model="transaccionForm.descripcion" />
        </el-form-item>
        <el-form-item label="Categoría">
          <el-select
            v-model="transaccionForm.categoria"
            placeholder="Seleccione categoría"
          >
            <el-option
              v-for="cat in categoriasPorTipo"
              :key="cat.valor"
              :label="cat.nombre"
              :value="cat.valor"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="guardarTransaccion">
            {{ modoEdicion ? "Guardar cambios" : "Crear" }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import api from "@/services/api";
import { ElMessage } from "element-plus";
import moment from "moment";

export default {
  name: "TransaccionesView",
  data() {
    return {
      transacciones: [],
      dialogVisible: false,
      modoEdicion: false,
      transaccionForm: {
        id: null,
        tipo: "",
        monto: 0,
        fecha: "",
        descripcion: "",
        categoria: "",
      },
      tiposFormateados: {
        ingreso: "Ingreso",
        gasto: "Gasto",
        transferencia_recibida: "Transf. Recibida",
        transferencia_emitida: "Transf. Emitida",
      },
      categoriasIngresos: [
        { nombre: "Salario", valor: "salario" },
        { nombre: "Freelance", valor: "freelance" },
        { nombre: "Otros ingresos", valor: "otros_ingresos" },
      ],
      categoriasGastos: [
        { nombre: "Alimentación", valor: "alimentacion" },
        { nombre: "Vivienda", valor: "vivienda" },
        { nombre: "Transporte", valor: "transporte" },
        { nombre: "Servicios", valor: "servicios" },
        { nombre: "Ocio", valor: "ocio" },
        { nombre: "Salud", valor: "salud" },
        { nombre: "Educación", valor: "educacion" },
        { nombre: "Otros gastos", valor: "otros_gastos" },
      ],
      categoriasTransferencias: [
        { nombre: "Transferencia Bancaria", valor: "transferencia_bancaria" },
        { nombre: "Bizum", valor: "bizum" },
      ],
      categoriasFormateadas: {
        // Ingresos
        salario: "Salario",
        freelance: "Freelance",
        otros_ingresos: "Otros Ingresos",

        // Gastos
        alimentacion: "Alimentación",
        vivienda: "Vivienda",
        transporte: "Transporte",
        servicios: "Servicios",
        ocio: "Ocio",
        salud: "Salud",
        educacion: "Educación",
        otros_gastos: "Otros Gastos",

        // Transferencias
        transferencia_bancaria: "Transf. Bancaria",
        bizum: "Bizum",
      },
    };
  },
  computed: {
    transaccionesFiltradas() {
      return this.transacciones.filter((t) =>
        [
          "ingreso",
          "gasto",
          "transferencia_recibida",
          "transferencia_emitida",
        ].includes(t.tipo)
      );
    },
    categoriasPorTipo() {
      switch (this.transaccionForm.tipo) {
        case "ingreso":
          return this.categoriasIngresos;
        case "gasto":
          return this.categoriasGastos;
        case "transferencia_recibida":
        case "transferencia_emitida":
          return this.categoriasTransferencias;
        default:
          return [];
      }
    },
  },
  watch: {
    "transaccionForm.tipo"() {
      this.transaccionForm.categoria = "";
    },
  },
  methods: {
    formatCurrency(value) {
      return new Intl.NumberFormat("es-ES", {
        style: "currency",
        currency: "EUR",
      }).format(value);
    },
    formatDate(date) {
      return moment(date).format("DD/MM/YYYY");
    },
    async obtenerTransacciones() {
      try {
        const response = await api.get("/transacciones/");
        this.transacciones = response.data;
      } catch (error) {
        console.error("Error al obtener transacciones:", error);
        ElMessage.error("Error al cargar las transacciones");
      }
    },
    editarTransaccion(transaccion) {
      this.modoEdicion = true;
      this.transaccionForm = {
        ...transaccion,
        fecha: moment(transaccion.fecha).toDate(),
      };
      this.dialogVisible = true;
    },
    async guardarTransaccion() {
      try {
        const transaccion = {
          ...this.transaccionForm,
          fecha: moment(this.transaccionForm.fecha).format("YYYY-MM-DD"),
        };

        if (this.modoEdicion) {
          await api.put(`/transacciones/${transaccion.id}`, transaccion);
          ElMessage.success("Transacción actualizada exitosamente");
        } else {
          await api.post("/transacciones/", transaccion);
          ElMessage.success("Transacción creada exitosamente");
        }

        this.dialogVisible = false;
        this.obtenerTransacciones();
      } catch (error) {
        console.error("Error al guardar transacción:", error);
        ElMessage.error(
          this.modoEdicion
            ? "Error al actualizar la transacción"
            : "Error al crear la transacción"
        );
      }
    },
    formatTipo(tipo) {
      return this.tiposFormateados[tipo] || tipo;
    },
    formatCategoria(categoria) {
      return this.categoriasFormateadas[categoria] || categoria;
    },
  },
  mounted() {
    this.obtenerTransacciones();
  },
};
</script>

<style scoped>
.transacciones {
  padding: 20px;
}

/* Asegura que el texto no se rompa en múltiples líneas */
.el-table .cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
