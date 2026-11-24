"""Xác minh danh tính Google qua OpenID Connect và PKCE."""

from dataclasses import dataclass
from functools import lru_cache
from hmac import compare_digest

from authlib.integrations.starlette_client import OAuth
from authlib.oidc.core import CodeIDToken

from app.config.settings import Config

_GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")


@dataclass(frozen=True, slots=True)
class GoogleIdentity:
    sub: str
    email: str
    email_verified: bool


class GoogleOIDC:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.redirect_uri = redirect_uri
        self.client_id = client_id

        oauth = OAuth()
        self.client = oauth.register(
            "google",
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            access_token_url="https://oauth2.googleapis.com/token",
            jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
            id_token_signing_alg_values_supported=["RS256"],
            client_kwargs={
                "scope": "openid email",
                "code_challenge_method": "S256",
                "token_endpoint_auth_method": "client_secret_post",
                "timeout": 10,
            },
        )

    async def authorization_url(self, *, state: str, nonce: str, code_verifier: str) -> str:
        result = await self.client.create_authorization_url(
            self.redirect_uri, state=state, nonce=nonce, code_verifier=code_verifier
        )
        return result["url"]

    async def exchange_code(self, *, code: str, nonce: str, code_verifier: str) -> GoogleIdentity:
        token = await self.client.fetch_access_token(
            redirect_uri=self.redirect_uri,
            code=code,
            grant_type="authorization_code",
            code_verifier=code_verifier,
        )
        claims = await self.client.parse_id_token(
            token,
            nonce=nonce,
            claims_options={
                "iss": {"essential": True, "values": list(_GOOGLE_ISSUERS)},
                "aud": {"essential": True, "value": self.client_id},
            },
            claims_cls=CodeIDToken,
            leeway=30,
        )
        claim_nonce = claims.get("nonce")
        if not isinstance(claim_nonce, str) or not compare_digest(
            claim_nonce.encode("utf-8"), nonce.encode("ascii")
        ):
            raise ValueError("Invalid Google nonce")

        sub = claims.get("sub")
        if not isinstance(sub, str) or not sub.strip() or len(sub) > 255:
            raise ValueError("Invalid Google subject")
        email = claims.get("email")
        return GoogleIdentity(
            sub=sub,
            email=email if isinstance(email, str) else "",
            email_verified=claims.get("email_verified") is True,
        )


@lru_cache(maxsize=1)
def get_google_oidc() -> GoogleOIDC:
    if not Config.GOOGLE_CLIENT_ID or not Config.GOOGLE_CLIENT_SECRET or not Config.GOOGLE_REDIRECT_URI:
        raise RuntimeError("Google OIDC client and callback configuration are required")
    return GoogleOIDC(
        Config.GOOGLE_CLIENT_ID,
        Config.GOOGLE_CLIENT_SECRET,
        str(Config.GOOGLE_REDIRECT_URI),
    )
