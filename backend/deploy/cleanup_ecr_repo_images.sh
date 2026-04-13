#!/usr/bin/env bash
set -e

ECR_IMAGE_URI="${1:?usage: cleanup_ecr_repo_images.sh <registry/repo:tag>}"
REPO="${ECR_IMAGE_URI%:*}"

IN_USE=$(docker ps -q | xargs docker inspect --format '{{.Image}}' 2>/dev/null | sort -u || true)

while IFS= read -r iid; do
  [ -z "$iid" ] && continue
  echo "$IN_USE" | grep -qxF "$iid" && continue
  docker rmi "$iid" 2>/dev/null || true
done < <(docker images "$REPO" --no-trunc --format "{{.ID}}" | sort -u)
