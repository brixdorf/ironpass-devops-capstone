{{- define "ironpass.name" -}}
{{- .Release.Name -}}
{{- end -}}

{{- define "ironpass.labels" -}}
app.kubernetes.io/name: ironpass
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{- define "ironpass.selector" -}}
app.kubernetes.io/name: ironpass
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "ironpass.dbSecret" -}}
{{ include "ironpass.name" . }}-postgres
{{- end -}}
