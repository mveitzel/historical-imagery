

library(foreign)

##---------------------IB------------------------

## IB 1948 image
##-----------------
aa1948<-read.dbf("IB/cov48randPointsIB_assessed.dbf")
aa1948<-subset(aa1948,!is.na(aa1948$ActualCl))
# error matrix
err1948<-table(aa1948$AssignCl,aa1948$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod1948<-round(100*diag(err1948)/table(aa1948$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user1948<-round(100*diag(err1948)/table(aa1948$AssignCl),2)
# kappa statistic
kappa1948<-(nrow(aa1948)*sum(diag(err1948))-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))/(nrow(aa1948)*nrow(aa1948)-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))
# overall accuracy
acc1948<-sum(diag(err1948))/nrow(aa1948)

err1948
prod1948
user1948
kappa1948
acc1948

## IB 2009 image
##-----------------
aa2009<-read.dbf("IB/cov09randPointsIB_assessed.dbf")
aa2009<-subset(aa2009,!is.na(aa2009$ActualCl))
# error matrix
err2009<-table(aa2009$AssignCl,aa2009$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod2009<-round(100*diag(err2009)/table(aa2009$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user2009<-round(100*diag(err2009)/table(aa2009$AssignCl),2)
# kappa statistic
kappa2009<-(nrow(aa2009)*sum(diag(err2009))-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))/(nrow(aa2009)*nrow(aa2009)-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))
# overall accuracy
acc2009<-sum(diag(err2009))/nrow(aa2009)

err2009
prod2009
user2009
kappa2009
acc2009

##---------------------BH------------------------


## BH 1948 image
##-----------------
aa1948<-read.dbf("BH/cov48randPointsBH_assessed.dbf")
aa1948<-subset(aa1948,!is.na(aa1948$ActualCl))
# error matrix
err1948<-table(aa1948$AssignCl,aa1948$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod1948<-round(100*diag(err1948)/table(aa1948$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user1948<-round(100*diag(err1948)/table(aa1948$AssignCl),2)
# kappa statistic
kappa1948<-(nrow(aa1948)*sum(diag(err1948))-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))/(nrow(aa1948)*nrow(aa1948)-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))
# overall accuracy
acc1948<-sum(diag(err1948))/nrow(aa1948)

err1948
prod1948
user1948
kappa1948
acc1948

## BH 2009 image
##-----------------
aa2009<-read.dbf("BH/cov09randPointsBH_assessed.dbf")
aa2009<-subset(aa2009,!is.na(aa2009$ActualCl))
# error matrix
err2009<-table(aa2009$AssignCl,aa2009$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod2009<-round(100*diag(err2009)/table(aa2009$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user2009<-round(100*diag(err2009)/table(aa2009$AssignCl),2)
# kappa statistic
kappa2009<-(nrow(aa2009)*sum(diag(err2009))-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))/(nrow(aa2009)*nrow(aa2009)-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))
# overall accuracy
acc2009<-sum(diag(err2009))/nrow(aa2009)

err2009
prod2009
user2009
kappa2009
acc2009



##---------------------BM------------------------


## BM 1948 image
##-----------------
aa1948<-read.dbf("BM/cov48randPointsBM_assessed.dbf")
aa1948<-subset(aa1948,!is.na(aa1948$ActualCl))
# error matrix
err1948<-table(aa1948$AssignCl,aa1948$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod1948<-round(100*diag(err1948)/table(aa1948$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user1948<-round(100*diag(err1948)/table(aa1948$AssignCl),2)
# kappa statistic
kappa1948<-(nrow(aa1948)*sum(diag(err1948))-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))/(nrow(aa1948)*nrow(aa1948)-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))
# overall accuracy
acc1948<-sum(diag(err1948))/nrow(aa1948)

err1948
prod1948
user1948
kappa1948
acc1948

## BM 2009 image
##-----------------
aa2009<-read.dbf("BM/cov09randPointsBM_assessed.dbf")
aa2009<-subset(aa2009,!is.na(aa2009$ActualCl))
# error matrix
err2009<-table(aa2009$AssignCl,aa2009$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod2009<-round(100*diag(err2009)/table(aa2009$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user2009<-round(100*diag(err2009)/table(aa2009$AssignCl),2)
# kappa statistic
kappa2009<-(nrow(aa2009)*sum(diag(err2009))-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))/(nrow(aa2009)*nrow(aa2009)-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))
# overall accuracy
acc2009<-sum(diag(err2009))/nrow(aa2009)

err2009
prod2009
user2009
kappa2009
acc2009



##---------------------WC------------------------


## WC 1948 image
##-----------------
aa1948<-read.dbf("WC/cov48randPointsWC_assessed.dbf")
aa1948<-subset(aa1948,!is.na(aa1948$ActualCl))
# error matrix
err1948<-table(aa1948$AssignCl,aa1948$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod1948<-round(100*diag(err1948)/table(aa1948$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user1948<-round(100*diag(err1948)/table(aa1948$AssignCl),2)
# kappa statistic
kappa1948<-(nrow(aa1948)*sum(diag(err1948))-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))/(nrow(aa1948)*nrow(aa1948)-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))
# overall accuracy
acc1948<-sum(diag(err1948))/nrow(aa1948)

err1948
prod1948
user1948
kappa1948
acc1948

## WC 2009 image
##-----------------
aa2009<-read.dbf("WC/cov09randPointsWC_assessed.dbf")
aa2009<-subset(aa2009,!is.na(aa2009$ActualCl))
# error matrix
err2009<-table(aa2009$AssignCl,aa2009$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod2009<-round(100*diag(err2009)/table(aa2009$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user2009<-round(100*diag(err2009)/table(aa2009$AssignCl),2)
# kappa statistic
kappa2009<-(nrow(aa2009)*sum(diag(err2009))-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))/(nrow(aa2009)*nrow(aa2009)-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))
# overall accuracy
acc2009<-sum(diag(err2009))/nrow(aa2009)

err2009
prod2009
user2009
kappa2009
acc2009

##---------------------all together------------------------


## 1948 images
##-----------------
aa1948<-read.dbf("IB/cov48randPointsIB_assessed.dbf")
aa1948<-subset(aa1948,!is.na(aa1948$ActualCl))
aa<-read.dbf("BM/cov48randPointsBM_assessed.dbf")
aa<-subset(aa,!is.na(aa$ActualCl))
aa1948<-rbind(aa, aa1948)
aa<-read.dbf("BH/cov48randPointsBH_assessed.dbf")
aa<-subset(aa,!is.na(aa$ActualCl))
aa1948<-rbind(aa, aa1948)
aa<-read.dbf("WC/cov48randPointsWC_assessed.dbf")
aa<-subset(aa,!is.na(aa$ActualCl))
aa1948<-rbind(aa, aa1948)

summary(aa1948)

# error matrix
err1948<-table(aa1948$AssignCl,aa1948$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod1948<-round(100*diag(err1948)/table(aa1948$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user1948<-round(100*diag(err1948)/table(aa1948$AssignCl),2)
# kappa statistic
kappa1948<-(nrow(aa1948)*sum(diag(err1948))-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))/(nrow(aa1948)*nrow(aa1948)-sum(table(aa1948$ActualCl)*table(aa1948$AssignCl)))
# overall accuracy
acc1948<-sum(diag(err1948))/nrow(aa1948)

err1948
prod1948
user1948
kappa1948
acc1948

## 2009 images
##-----------------
aa2009<-read.dbf("IB/cov09randPointsIB_assessed.dbf")
summary(aa2009)
aa2009<-subset(aa2009,!is.na(aa2009$ActualCl))
aa<-read.dbf("BM/cov09randPointsBM_assessed.dbf")
summary(aa)
aa<-subset(aa,!is.na(aa$ActualCl))
aa2009<-rbind(aa, aa2009)
aa<-read.dbf("BH/cov09randPointsBH_assessed.dbf")
summary(aa)
aa<-subset(aa,!is.na(aa$ActualCl))
aa2009<-rbind(aa, aa2009)
aa<-read.dbf("WC/cov09randPointsWC_assessed.dbf")
summary(aa)
aa<-subset(aa,!is.na(aa$ActualCl))
aa2009<-rbind(aa, aa2009)
aa<-read.dbf("IB/Additional_2009_Grass_Points.dbf")
summary(aa)
aa<-subset(aa,!is.na(aa$ActualCl))
aa2009<-rbind(aa, aa2009)
aa<-read.dbf("BM/Additional_2009_Grass_Points.dbf")
summary(aa)
aa<-subset(aa,!is.na(aa$ActualCl))
aa2009<-rbind(aa, aa2009)
aa2009$AssignCl<-as.factor(as.character(aa2009$AssignCl))
summary(aa2009)

# error matrix
err2009<-table(aa2009$AssignCl,aa2009$ActualCl)
# producer's accuracy (omission) - correctly classified percentage of ground truth samples tested
prod2009<-round(100*diag(err2009)/table(aa2009$ActualCl),2)
# user's accuracy (commission) - correctly classified percentage of remotely sensed categories tested
user2009<-round(100*diag(err2009)/table(aa2009$AssignCl),2)
# kappa statistic
kappa2009<-(nrow(aa2009)*sum(diag(err2009))-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))/(nrow(aa2009)*nrow(aa2009)-sum(table(aa2009$ActualCl)*table(aa2009$AssignCl)))
# overall accuracy
acc2009<-sum(diag(err2009))/nrow(aa2009)

err2009
prod2009
user2009
kappa2009
acc2009

 