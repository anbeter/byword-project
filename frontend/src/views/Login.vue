<script setup>
import api from "../services/api";

async function login() {
  const res = await api.post("/token/", {
    username: "admin",
    password: "tdatsl2"
  });

  localStorage.setItem("token", res.data.access);
}
</script>

<template>
  <button @click="login">Login</button>
</template>