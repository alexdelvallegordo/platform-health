{{- define "platform-health.name" -}}
platform-health
{{- end }}

{{- define "platform-health.fullname" -}}
{{ .Release.Name }}
{{- end }}

{{- define "platform-health.labels" -}}
app.kubernetes.io/name: {{ include "platform-health.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
