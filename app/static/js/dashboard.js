const STATUS_ENDPOINT = "/api/v1/status";
const REFRESH_INTERVAL = 5000;


const elements = {
  overall: document.getElementById("overall-status"),
  overallText: document.getElementById("overall-status-text"),

  componentCount: document.getElementById("component-count"),
  healthyCount: document.getElementById("healthy-count"),
  issueCount: document.getElementById("issue-count"),
  lastCheck: document.getElementById("last-check"),

  automation: document.getElementById("automation-components"),
  kubernetes: document.getElementById("kubernetes-components"),

  refreshIndicator: document.getElementById("refresh-indicator"),
  refreshText: document.getElementById("refresh-text"),
};


function humanStatus(status) {
  if (!status) {
    return "Unknown";
  }

  return (
    status.charAt(0).toUpperCase()
    + status.slice(1)
  );
}


function formatTime(timestamp) {
  const date = new Date(timestamp);

  return date.toLocaleTimeString(
    [],
    {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }
  );
}


function componentMetric(component) {
  if (component.latency_ms !== null &&
      component.latency_ms !== undefined) {

    return `${component.latency_ms.toFixed(1)} ms`;
  }

  const metadata = component.metadata || {};

  if (
    metadata.ready_replicas !== undefined &&
    metadata.desired_replicas !== undefined
  ) {
    return (
      `${metadata.ready_replicas}/`
      + `${metadata.desired_replicas} ready`
    );
  }

  if (metadata.ready === true) {
    return "Ready";
  }

  if (metadata.ready === false) {
    return "Not Ready";
  }

  return "";
}


function componentDetail(component) {
  if (component.detail) {
    return component.detail;
  }

  const metadata = component.metadata || {};

  if (metadata.version) {
    return `Version ${metadata.version}`;
  }

  if (metadata.nodes !== undefined) {
    return `${metadata.nodes} node(s) detected`;
  }

  return "Operating normally";
}


function createComponentCard(component) {
  const card = document.createElement("article");

  card.className =
    `component-card component-status-${component.status}`;


  const primary = document.createElement("div");
  primary.className = "component-primary";


  const indicator = document.createElement("span");
  indicator.className = "component-indicator";


  const information = document.createElement("div");


  const name = document.createElement("h3");
  name.className = "component-name";
  name.textContent = component.name;


  const detail = document.createElement("p");
  detail.className = "component-detail";
  detail.textContent = componentDetail(component);


  information.appendChild(name);
  information.appendChild(detail);

  primary.appendChild(indicator);
  primary.appendChild(information);


  const secondary = document.createElement("div");
  secondary.className = "component-secondary";


  const status = document.createElement("div");
  status.className = "component-status-text";
  status.textContent = humanStatus(component.status);


  const metric = document.createElement("div");
  metric.className = "component-metric";
  metric.textContent = componentMetric(component);


  secondary.appendChild(status);
  secondary.appendChild(metric);

  card.appendChild(primary);
  card.appendChild(secondary);

  return card;
}


function renderGroup(container, components) {
  container.replaceChildren();

  if (components.length === 0) {
    const empty = document.createElement("div");

    empty.className = "empty-state";
    empty.textContent = "No components available.";

    container.appendChild(empty);

    return;
  }

  for (const component of components) {
    container.appendChild(
      createComponentCard(component)
    );
  }
}


function renderSummary(data) {
  const components = data.components;

  const healthy = components.filter(
    component => component.status === "healthy"
  ).length;

  const issues = components.length - healthy;


  elements.componentCount.textContent =
    components.length;

  elements.healthyCount.textContent =
    healthy;

  elements.issueCount.textContent =
    issues;

  elements.lastCheck.textContent =
    formatTime(data.checked_at);
}


function renderOverall(status) {
  elements.overall.className =
    `overall-status status-${status}`;

  elements.overallText.textContent =
    humanStatus(status);
}


function renderDashboard(data) {
  renderOverall(data.status);
  renderSummary(data);

  const automationComponents =
    data.components.filter(
      component =>
        component.group === "automation-platform"
    );

  const kubernetesComponents =
    data.components.filter(
      component =>
        component.group === "kubernetes"
    );


  renderGroup(
    elements.automation,
    automationComponents
  );

  renderGroup(
    elements.kubernetes,
    kubernetesComponents
  );


  elements.refreshIndicator.classList.remove(
    "error"
  );

  elements.refreshText.textContent =
    "Live monitoring active";
}


function renderConnectionError() {
  elements.overall.className =
    "overall-status status-down";

  elements.overallText.textContent =
    "Unavailable";

  elements.refreshIndicator.classList.add(
    "error"
  );

  elements.refreshText.textContent =
    "Unable to retrieve platform status";
}


async function refreshStatus() {
  try {
    const response = await fetch(
      STATUS_ENDPOINT,
      {
        cache: "no-store",
      }
    );

    if (!response.ok) {
      throw new Error(
        `Status API returned ${response.status}`
      );
    }

    const data = await response.json();

    renderDashboard(data);

  } catch (error) {
    console.error(
      "Platform status refresh failed:",
      error
    );

    renderConnectionError();
  }
}


refreshStatus();

setInterval(
  refreshStatus,
  REFRESH_INTERVAL
);
