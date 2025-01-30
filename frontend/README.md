# Overview 
This is the Angular frontend web application for LitReview.

## Setup
1. Install [NVM](https://github.com/nvm-sh/nvm) for your platform (Linux is much easier)
2. Install [NPM](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
3. In the `litreview` root, run `npm install`

## Run tasks

To run the dev server for your app, use:

```sh
npx nx serve litreview
```

To create a production bundle:

```sh
npx nx build litreview
```

To see all available targets to run for a project, run:

```sh
npx nx show project litreview
```