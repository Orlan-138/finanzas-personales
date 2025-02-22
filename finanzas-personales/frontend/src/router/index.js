import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";
import LoginView from "../views/LoginView.vue";

const routes = [
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/",
    name: "dashboard",
    component: DashboardView,
    meta: { requiresAuth: true },
  },
  {
    path: "/transacciones",
    name: "transacciones",
    component: () => import("../views/TransaccionesView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/inversiones",
    name: "inversiones",
    component: () => import("../views/InversionesView.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/creditos",
    name: "creditos",
    component: () => import("../views/CreditosView.vue"),
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!localStorage.getItem("token")) {
      next("/login");
      return;
    }
  }
  next();
});

export default router;
