## Запустить для разработки

1. `pnpm install`
2. `pnpm approve-builds`
3. `pnpm run dev`

## Запустить в продакшен

1. `docker build -t chococore .`
2. `docker run -d -p 3000:3000 -e NODE_ENV=production chococore`
