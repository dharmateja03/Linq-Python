# API Surface

## Chats

- `client.chats.create(body)` -> `POST /v3/chats`
- `client.chats.get(chat_id)` -> `GET /v3/chats/{chatId}`
- `client.chats.update(chat_id, body)` -> `PUT /v3/chats/{chatId}`
- `client.chats.list(query)` -> `GET /v3/chats`
- `client.chats.list_auto_paging(query)`
- `client.chats.mark_as_read(chat_id)` -> `POST /v3/chats/{chatId}/read`
- `client.chats.send_voicememo(chat_id, body)` -> `POST /v3/chats/{chatId}/voicememo`
- `client.chats.share_contact_card(chat_id)` -> `POST /v3/chats/{chatId}/share_contact_card`

### Participants

- `client.chats.participants.add(chat_id, body)` -> `POST /v3/chats/{chatId}/participants`
- `client.chats.participants.remove(chat_id, body)` -> `DELETE /v3/chats/{chatId}/participants`

### Typing

- `client.chats.typing.start(chat_id)` -> `POST /v3/chats/{chatId}/typing`
- `client.chats.typing.stop(chat_id)` -> `DELETE /v3/chats/{chatId}/typing`

### Chat Messages

- `client.chats.messages.list(chat_id, query)` -> `GET /v3/chats/{chatId}/messages`
- `client.chats.messages.list_auto_paging(chat_id, query)`
- `client.chats.messages.send(chat_id, body)` -> `POST /v3/chats/{chatId}/messages`

## Messages

- `client.messages.get(message_id)` -> `GET /v3/messages/{messageId}`
- `client.messages.update(message_id, body)` -> `PATCH /v3/messages/{messageId}`
- `client.messages.delete(message_id)` -> `DELETE /v3/messages/{messageId}`
- `client.messages.add_reaction(message_id, body)` -> `POST /v3/messages/{messageId}/reactions`
- `client.messages.list_messages_thread(message_id, query)` -> `GET /v3/messages/{messageId}/thread`
- `client.messages.list_messages_thread_auto_paging(message_id, query)`

## Attachments

- `client.attachments.create(body)` -> `POST /v3/attachments`
- `client.attachments.get(attachment_id)` -> `GET /v3/attachments/{attachmentId}`

## Phone Numbers

- `client.phonenumbers.list()` -> `GET /v3/phonenumbers` (deprecated)
- `client.phone_numbers.list()` -> `GET /v3/phone_numbers`

## Webhook Events

- `client.webhook_events.list()` -> `GET /v3/webhook-events`

## Webhook Subscriptions

- `client.webhook_subscriptions.create(body)` -> `POST /v3/webhook-subscriptions`
- `client.webhook_subscriptions.get(subscription_id)` -> `GET /v3/webhook-subscriptions/{subscriptionId}`
- `client.webhook_subscriptions.update(subscription_id, body)` -> `PUT /v3/webhook-subscriptions/{subscriptionId}`
- `client.webhook_subscriptions.list()` -> `GET /v3/webhook-subscriptions`
- `client.webhook_subscriptions.delete(subscription_id)` -> `DELETE /v3/webhook-subscriptions/{subscriptionId}`

## Capability

- `client.capability.check_imessage(body)` -> `POST /v3/capability/check_imessage`
- `client.capability.check_rcs(body)` -> `POST /v3/capability/check_rcs`

## Webhooks Utility

- `client.webhooks.events(payload)`
- `client.webhooks.verify_signature(signing_secret, payload, timestamp, signature)`
- `client.webhooks.verify_headers(signing_secret, payload, headers)`
