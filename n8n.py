import json

# --- WORKFLOW 1 : ACQUISITION (HEURES CREUSES) ---
workflow_a = {
    "name": "🟢 Arkose - Acquisition Heures Creuses",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "weeks",
                            "intervalValue": 1
                        }
                    ]
                }
            },
            "name": "Schedule Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1,
            "position": [100, 300]
        },
        {
            "parameters": {
                "operation": "subtract",
                "duration": 7,
                "unit": "days"
            },
            "name": "Date Calculation",
            "type": "n8n-nodes-base.dateTime",
            "typeVersion": 1,
            "position": [300, 300]
        },
        {
            "parameters": {
                "authentication": "oAuth2",
                "operation": "lookup",
                "sheetId": "METTRE_ID_SHEET_ICI",
                "range": "A:Z",
                "lookupColumn": "Date",
                "lookupValue": "={{$node[\"Date Calculation\"].json[\"data\"]}}"
            },
            "name": "Read Google Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 2,
            "position": [500, 300],
            "notes": "Connecter ici votre fichier de données"
        },
        {
            "parameters": {
                "conditions": {
                    "number": [
                        {
                            "value1": "={{$json[\"Passage\"]}}",
                            "operation": "smaller",
                            "value2": 160
                        }
                    ]
                }
            },
            "name": "If Capacity < 40%",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [700, 300]
        },
        {
            "parameters": {
                "subject": "🧗 Promo Grimpe demain !",
                "content": "C'est le moment de grimper au calme...",
                "toEmail": "list-subscribers@arkose.com"
            },
            "name": "Send Email",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 1,
            "position": [900, 200]
        }
    ],
    "connections": {
        "Schedule Trigger": {"main": [[{"node": "Date Calculation", "type": "main", "index": 0}]]},
        "Date Calculation": {"main": [[{"node": "Read Google Sheets", "type": "main", "index": 0}]]},
        "Read Google Sheets": {"main": [[{"node": "If Capacity < 40%", "type": "main", "index": 0}]]},
        "If Capacity < 40%": {"main": [[{"node": "Send Email", "type": "main", "index": 0}]]}
    }
}

# --- WORKFLOW 2 : CONVERSION RESTAURATION ---
workflow_b = {
    "name": "🟡 Arkose - Conversion Restauration",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "days",
                            "intervalValue": 1
                        }
                    ]
                }
            },
            "name": "Schedule Daily",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1,
            "position": [100, 300]
        },
        {
            "parameters": {
                "operation": "subtract",
                "duration": 1,
                "unit": "days"
            },
            "name": "Get Yesterday",
            "type": "n8n-nodes-base.dateTime",
            "typeVersion": 1,
            "position": [300, 300]
        },
        {
            "parameters": {
                "authentication": "oAuth2",
                "operation": "lookup",
                "sheetId": "METTRE_ID_SHEET_ICI",
                "lookupColumn": "Date",
                "lookupValue": "={{$json[\"data\"]}}"
            },
            "name": "Fetch Data",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "jsCode": "return {\n  json: {\n    ratio: $input.item.json.Plat / $input.item.json.Passage\n  }\n}"
            },
            "name": "Calculate Ratio",
            "type": "n8n-nodes-base.code",
            "typeVersion": 1,
            "position": [700, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "number": [
                        {
                            "value1": "={{$json[\"ratio\"]}}",
                            "operation": "smaller",
                            "value2": 0.15
                        }
                    ]
                }
            },
            "name": "If Ratio < 15%",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [900, 300]
        },
        {
            "parameters": {
                "channel": "marketing-alerts",
                "text": "⚠️ Alerte Conversion : Seulement {{$json[\"ratio\"]*100}}% de conversion hier. Activez la promo Burger !"
            },
            "name": "Slack Alert",
            "type": "n8n-nodes-base.slack",
            "typeVersion": 1,
            "position": [1100, 200]
        }
    ],
    "connections": {
        "Schedule Daily": {"main": [[{"node": "Get Yesterday", "type": "main", "index": 0}]]},
        "Get Yesterday": {"main": [[{"node": "Fetch Data", "type": "main", "index": 0}]]},
        "Fetch Data": {"main": [[{"node": "Calculate Ratio", "type": "main", "index": 0}]]},
        "Calculate Ratio": {"main": [[{"node": "If Ratio < 15%", "type": "main", "index": 0}]]},
        "If Ratio < 15%": {"main": [[{"node": "Slack Alert", "type": "main", "index": 0}]]}
    }
}

# --- WORKFLOW 3 : FIDÉLISATION (RETARGETING) ---
workflow_c = {
    "name": "🔵 Arkose - Fidélisation J+21",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "field": "days",
                            "intervalValue": 1
                        }
                    ]
                }
            },
            "name": "Daily Trigger",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1,
            "position": [100, 300]
        },
        {
            "parameters": {
                "authentication": "oAuth2",
                "operation": "getAll",
                "sheetId": "METTRE_ID_SHEET_CLIENTS_ICI"
            },
            "name": "Get All Clients",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 2,
            "position": [300, 300]
        },
        {
            "parameters": {
                "jsCode": "const results = [];\nconst today = new Date();\n\nfor (const item of $input.all()) {\n  const lastVisit = new Date(item.json.Derniere_Visite);\n  const diffTime = Math.abs(today - lastVisit);\n  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); \n  \n  if (diffDays === 21) {\n    results.push({json: item.json});\n  }\n}\n\nreturn results;"
            },
            "name": "Filter 21 Days",
            "type": "n8n-nodes-base.code",
            "typeVersion": 1,
            "position": [500, 300]
        },
        {
            "parameters": {
                "subject": "👋 Ça fait longtemps !",
                "content": "Bonjour {{$json[\"Prenom\"]}}, cela fait 3 semaines que nous ne t'avons pas vu...",
                "toEmail": "={{$json[\"Email\"]}}"
            },
            "name": "Email Relance",
            "type": "n8n-nodes-base.emailSend",
            "typeVersion": 1,
            "position": [700, 300]
        }
    ],
    "connections": {
        "Daily Trigger": {"main": [[{"node": "Get All Clients", "type": "main", "index": 0}]]},
        "Get All Clients": {"main": [[{"node": "Filter 21 Days", "type": "main", "index": 0}]]},
        "Filter 21 Days": {"main": [[{"node": "Email Relance", "type": "main", "index": 0}]]}
    }
}

# Save files
with open('n8n_arkose_acquisition.json', 'w') as f:
    json.dump(workflow_a, f, indent=2)

with open('n8n_arkose_conversion.json', 'w') as f:
    json.dump(workflow_b, f, indent=2)

with open('n8n_arkose_fidelisation.json', 'w') as f:
    json.dump(workflow_c, f, indent=2)