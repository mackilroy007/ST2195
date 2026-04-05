---
title: "PartA"
output: html_document
---
# Install tidyverse if not already installed (replace with ggplot2 if you want more lean variant)

if (!require(tidyverse)) {
    install.packages("tidyverse")
    library(tidyverse)
}

#Read python code, explenations there
x0 <- 0.0
N <- 10000
s <- 1.0

xValue <- numeric(N + 1)
xValue[1] <- x0

# target distribtion - standard normal 
f <- function(x) {
    return(exp(-0.5 * x^2) / sqrt(2 * pi))
}

# log version to avoid numerial issues
logF <- function(x) {
    return(-0.5 * x^2 - 0.5 * log(2 * pi))
}

for (i in 2:(N + 1)) {
    xStar <- rnorm(1, mean=xValue[i-1], sd=s)
    logR <- logF(xStar) - logF(xValue[i-1])
    u <- runif(1, 0, 1)
    
    if (log(u) < logR) {
        xValue[i] <- xStar
    } else {
        xValue[i] <- xValue[i-1]
    }
}

---
#QUESTIONE: A
---   

samples <- xValue[2:length(xValue)]

sampleMean <- mean(samples)
sampleStandard <- sd(samples)

cat(sprintf("Sample mean: .4f", sampleMean))
cat(sprintf("Sample std diviation: .4f", sampleStandard))

png('metropolis-results.png', width=10, height=6, units='in', res=300)

hist(samples, breaks=50, freq=FALSE, col=rgb(0,0,1,0.6), 
     main='Metropolis-Hastings: Histogram, KDE and True Distribtion',
     xlab='x', ylab='Density', border='black')

kde <- density(samples)
lines(kde, col='red', lwd=2)

xTrue <- seq(-4, 4, length.out=1000)
yTrue <- sapply(xTrue, f)
lines(xTrue, yTrue, col='green', lty=2, lwd=2)

legend('topright', legend=c('Histogram', 'KDE', 'True f(x)'),
    col=c(rgb(0,0,1,0.6), 'red', 'green'), 
    lty=c(1,1,2), lwd=c(10,2,2))

grid()
dev.off()

cat("Plot saved: 'metropolis-results.png'")

---
#QUESTION B - gelman rubin diagonstic
---

# function to run a single chain
runChain <- function(x0, N, s, seed=NULL) {
    if (!is.null(seed)) {
        set.seed(seed)
    }
    
    xValues <- numeric(N + 1)
    xValues[1] <- x0
    
    for (i in 2:(N + 1)) {
        xStar <- rnorm(1, mean=xValues[i-1], sd=s)
        logR <- logF(xStar) - logF(xValues[i-1])
        u <- runif(1, 0, 1)
        
        if (log(u) < logR) {
            xValues[i] <- xStar
        } else {
            xValues[i] <- xValues[i-1]
        }
    }
    
    return(xValues[2:length(xValues)])
}

# calcualte R hat
calcRHat <- function(chains) {
    J <- length(chains)
    N <- length(chains[[1]])
    
    Mj <- sapply(chains, mean)
    Vj <- sapply(chains, var)
    
    W <- mean(Vj)
    M <- mean(Mj)
    B <- N / (J - 1) * sum((Mj - M)^2)
    
    RHat <- sqrt((B + W) / W)
    
    return(RHat)
}

Nb <- 2000
sb <- 0.001
Jb <- 4
burnin <- 500

cat(sprintf("Params: N= d, s= .3f, J= d, burn in= d", Nb, sb, Jb, burnin))

initValues <- c(-0.5, -0.2, 0.2, 0.5)
chains <- list()

cat("Running chains...")
for (j in 1:Jb) {
    totalChain <- runChain(x0=initValues[j], N=Nb+burnin, s=sb, seed=j*100)
    chain <- totalChain[(burnin+1):length(totalChain)]
    chains[[j]] <- chain
    cat(sprintf("  Chain d: x0=.1f, mean=.4f, std=.4f", j, initValues[j], mean(chain), sd(chain)))
}

rhat <- calcRHat(chains)
cat(sprintf("R-hat = .6f", rhat))
if (rhat < 1.05) {
    cat("YES Converged!!!! < 1.05")
} else {
    cat("NOT converged >= 1.05")
}

sValues <- seq(0.001, 1, length.out=50)
rHatValuess <- numeric(length(sValues))

cat("Computing... this takes a sec... come oooon")
for (idx in 1:length(sValues)) {
    chainsS <- list()
    for (j in 1:Jb) {
        totalChain <- runChain(x0=initValues[j], N=Nb+burnin, s=sValues[idx], seed=j*100)
        chain <- totalChain[(burnin+1):length(totalChain)]
        chainsS[[j]] <- chain
    }
    
    rHatS <- calcRHat(chainsS)
    rHatValuess[idx] <- rHatS
    
    if (idx %% 10 == 0) {
        cat(sprintf("Done!!!!", idx, length(sValues)))
    }
}

cat("Done computing!!!!")

png('gelman-rubin-diagnostic.png', width=12, height=7, units='in', res=300)

plot(sValues, rHatValuess, type='l', col='blue', lwd=2,
     xlab='Step size (s)', ylab='R-hat',
     main=sprintf('Gelman-Rubin Diagnostic (N=d, J=d chains)', Nb, Jb),
     cex.lab=1.2, cex.main=1.4)

abline(h=1.05, col='red', lty=2, lwd=2)
abline(h=1.0, col='green', lty=3, lwd=1.5)

sIndexes <- which.min(abs(sValues - 0.001))
points(sValues[sIndexes], rHatValuess[sIndexes], col='red', pch=19, cex=2)

legend('topright', 
       legend=c('R-hat', 'Convergence threshhold (1.05)', 'Perfect (1.0)',
                sprintf('s=0.001: R-hat=.4f', rHatValuess[sIndexes])),
       col=c('blue', 'red', 'green', 'red'), 
       lty=c(1,2,3,NA), lwd=c(2,2,1.5,NA), pch=c(NA,NA,NA,19),
       cex=0.9)

grid()
dev.off()

cat("Plot saved as 'gelman-rubin-diagnostic.png'")

cat(sprintf("Min R-hat: .6f at s=.4f", 
            min(rHatValuess), sValues[which.min(rHatValuess)]))
cat(sprintf("Max R-hat: .6f at s=.4f", 
            max(rHatValuess), sValues[which.max(rHatValuess)]))
convergedCount <- sum(rHatValuess < 1.05)
cat(sprintf("Converged s values: d/d", convergedCount, length(sValues)))

