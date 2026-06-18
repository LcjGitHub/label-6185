<template>
  <div class="layout">
    <header class="header">
      <router-link to="/" class="brand">
        <i class="pi pi-map" />
        <span>冷门徒步路线水源标记</span>
      </router-link>
      <nav class="nav">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          <i class="pi pi-chart-bar" />
          <span>概览</span>
        </router-link>
        <router-link to="/routes" class="nav-link" :class="{ active: $route.path.startsWith('/routes') }">
          <i class="pi pi-directions" />
          <span>路线</span>
        </router-link>
      </nav>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: system-ui, -apple-system, 'Segoe UI', sans-serif;
  background: #f4f6f9;
  color: #1e293b;
}

.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #1e3a5f;
  color: #fff;
  padding: 0.875rem 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: inherit;
  text-decoration: none;
  font-size: 1.125rem;
  font-weight: 600;
}

.brand:hover {
  opacity: 0.9;
}

.nav {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: 0.5rem;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
}

.main {
  flex: 1;
  padding: 1.5rem;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
}
</style>
