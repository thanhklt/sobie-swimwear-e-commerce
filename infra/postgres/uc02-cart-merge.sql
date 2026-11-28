-- Apply to an existing database before enabling UC-02 checkout.
CREATE TABLE IF NOT EXISTS shopping.cart_merge (
  cart_key     uuid NOT NULL REFERENCES shopping.cart (cart_key) ON DELETE CASCADE,
  merge_key    uuid NOT NULL,
  payload_hash char(64) NOT NULL,
  result       jsonb NOT NULL,
  PRIMARY KEY (cart_key, merge_key)
);
