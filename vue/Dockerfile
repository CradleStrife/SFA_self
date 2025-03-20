# for development

# FROM node:18

# # Set the working directory in the container
# WORKDIR /app

# # Copy package.json and package-lock.json
# COPY package*.json ./

# # Ensure clean installation of dependencies
# RUN npm install

# # Copy the rest of the application
# COPY . .

# # Expose port 5173 for Vite
# EXPOSE 5173

# # Run the application
# CMD ["npm", "run", "dev"]


# for production 

FROM node:18 AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY public /usr/share/nginx/html
EXPOSE 5173
CMD ["nginx", "-g", "daemon off;"]
