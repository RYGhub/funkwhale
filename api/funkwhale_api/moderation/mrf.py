"""
Inspired from the MRF logic from Pleroma, see https://docs-develop.pleroma.social/mrf.html
To support pluggable / customizable moderation using a programming language if
our exposed features aren't enough.
"""

import logging

import persisting_theory

logger = logging.getLogger("funkwhale.mrf")


class MRFException(Exception):
    pass


class Discard(MRFException):
    pass


class Skip(MRFException):
    pass


class Registry(persisting_theory.Registry):
    look_into = "mrf_policies"

    def __init__(self, name=""):
        self.name = name

        super().__init__()

    def apply(self, payload, **kwargs):
        policy_names = kwargs.pop("policies", [])
        if not policy_names:
            policies = self.items()
        else:
            logger.debug(
                "[MRF.%s] Running restricted list of policies %s…",
                self.name,
                ", ".join(policy_names),
            )
            policies = [(name, self[name]) for name in policy_names]
        updated = False
        for policy_name, policy in policies:
            logger.debug("[MRF.%s] Applying mrf policy '%s'…", self.name, policy_name)
            try:
                new_payload = policy(payload, **kwargs)
            except Skip as e:
                logger.debug(
                    "[MRF.%s] Skipped policy %s because '%s'",
                    self.name,
                    policy_name,
                    str(e),
                )
                continue
            except Discard as e:
                logger.info(
                    "[MRF.%s] Discarded message per policy '%s' because '%s'",
                    self.name,
                    policy_name,
                    str(e),
                )
                return (None, False)
            except Exception:
                logger.exception(
                    "[MRF.%s] Error while applying policy '%s'!", self.name, policy_name
                )
                continue
            if new_payload:
                updated = True
                payload = new_payload

        return payload, updated


inbox = Registry("inbox")
