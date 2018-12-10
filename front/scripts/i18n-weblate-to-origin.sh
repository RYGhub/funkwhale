#!/bin/bash -eux
integration_branch="translations-integration"
git remote add weblate https://translate.funkwhale.audio/git/funkwhale/front/ || echo "remote already exists"
git fetch weblate
git checkout weblate/develop
git reset --hard weblate/develop
git checkout -b $integration_branch || git checkout $integration_branch
git reset --hard weblate/develop
git push -f origin $integration_branch

echo "Branch created on pushed on origin/$integration_branch"
echo "Open a merge request by visiting https://dev.funkwhale.audio/funkwhale/funkwhale/merge_requests/new?merge_request%5Bsource_branch%5D=$integration_branch"
