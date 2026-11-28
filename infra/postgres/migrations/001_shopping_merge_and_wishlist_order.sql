-- Migration local / nhánh feature/shopping
-- [GD] Bổ sung schema cho UC-18 AC-10/11 và UC-38 AC-3 trên DB đã init trước đó.

ALTER TABLE shopping.wishlist_item
  ADD COLUMN IF NOT EXISTS wishlist_item_added_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS shopping.cart_merge_request (
  cart_merge_request_key           uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_merge_request_account_key   uuid        NOT NULL
    REFERENCES identity.account (account_key) ON DELETE CASCADE,
  cart_merge_request_id            varchar(64) NOT NULL,
  cart_merge_request_payload_hash  char(64)    NOT NULL,
  cart_merge_request_created_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT cart_merge_request_account_id_uq
    UNIQUE (cart_merge_request_account_key, cart_merge_request_id)
);
