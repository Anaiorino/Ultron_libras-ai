# Modelagem do Projeto - Jarvis Libras IA

## Entidade: Sign

A entidade `Sign` representa um sinal em Libras cadastrado no sistema.

| Campo | Tipo | Descrição |
|---|---|---|
| id | Integer | Identificador único do sinal |
| name | String | Nome do sinal |
| description | String | Descrição do sinal |
| video_path | String | Caminho do vídeo/animação do sinal |
| created_at | DateTime | Data de criação do registro |

## DER Simplificado

```txt
+----------------------+
|        Sign          |
+----------------------+
| id PK                |
| name                 |
| description          |
| video_path           |
| created_at           |
+----------------------+

+----------------------+
|        Sign          |
+----------------------+
| - id: int            |
| - name: string       |
| - description: str   |
| - video_path: str    |
| - created_at: date   |
+----------------------+

+----------------------+
|     SignService      |
+----------------------+
| + create_sign()      |
| + list_signs()       |
| + get_sign()         |
| + update_sign()      |
| + delete_sign()      |
+----------------------+