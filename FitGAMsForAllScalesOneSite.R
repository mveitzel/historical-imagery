################################################################
################################################################
# Final code to fit the models and create the scaling figures  #
################################################################
################################################################


################################################################
#------------Administrivia-------------
################################################################
rm(list=ls())

site <- "WC" # IB, BM, BH, WC
#specify username
path <-paste("C:/Users/",username,"/Dropbox/Professional/ConiferEncroachment/ChangeModeling/",site,"/",sep="")
setwd(path)

library(raster)
library(geoR)
library(spdep)
library(ncf)
library(mgcv)
library(nortest)
gamfit<-list()

gamfit.summary<-list()
mt.GAM<-list()
timings<-list()
num.knots<-list()
scaleparm<-list()
correl.GAM<-list()
sig.spat<-list()
resid.norm<-list()
PCA.variance<-list()
PCA.cor<-list()

################################################################
#---------------------loop through scales----------------------
################################################################
for (i in 10:2) {

	print(i)

	################################################################
	#-----------------read data and create variables-------------
	################################################################
	cc<-read.csv(paste("AllData_",site,"_",i,".csv",sep=""))

	nb.dist<-i*10
	nb.dist<-nb.dist*1.45 ## queen neighborhood

	cc$cov.pct.2009=cc$COVER2009/cc$CELL_AREA
	cc$cov.pct.1948=cc$COVER1948/cc$CELL_AREA
	
	# make standardized variables.
	cc$sELEV<-(cc$ELEV-mean(cc$ELEV))/sd(cc$ELEV)
	cc$sSLOPE<-(cc$SLOPE-mean(cc$SLOPE))/sd(cc$SLOPE)
	cc$sCURV<-(cc$CURV-mean(cc$CURV))/sd(cc$CURV)
	cc$sCURV_PROF<-(cc$CURV_PROF-mean(cc$CURV_PROF))/sd(cc$CURV_PROF)
	cc$sCURV_PLAN<-(cc$CURV_PLAN-mean(cc$CURV_PLAN))/sd(cc$CURV_PLAN)
	cc$sNORTHN<-(cc$NORTHN-mean(cc$NORTHN))/sd(cc$NORTHN)
	cc$sEASTN<-(cc$EASTN-mean(cc$EASTN))/sd(cc$EASTN)
	cc$sTMI<-(cc$TMI-mean(cc$TMI))/sd(cc$TMI)

	cc$sINSOL<-(cc$INSOL-mean(cc$INSOL))/sd(cc$INSOL)
	cc$sDISTRIDGE<-(cc$DISTRIDGE-mean(cc$DISTRIDGE))/sd(cc$DISTRIDGE)
	cc$sHEATIND<-(cc$HEATIND-mean(cc$HEATIND))/sd(cc$HEATIND)

	if(site!="WC")
		cc$sNEAR_DIST<-(cc$NEAR_DIST-mean(cc$NEAR_DIST))/sd(cc$NEAR_DIST)

	cc$cXCoord<-cc$XCoord-mean(cc$XCoord)
	cc$cYCoord<-cc$YCoord-mean(cc$YCoord)
	cc$cEASTING<-cc$EASTING-mean(cc$EASTING)
	cc$cNORTHING<-cc$NORTHING-mean(cc$NORTHING)

	#logit transform previous cover percent
	cc$CovPct<-cc$cov.pct.1948
	cc$CovPct[cc$CovPct<=0]<- 1e-6
	cc$CovPct[cc$CovPct>=1]<- 1- 1e-6
	cc$tCovPct1948<-log((cc$CovPct)/(1-cc$CovPct))
	# standardize it
	cc$stCovPct1948<-(cc$tCovPct1948-mean(cc$tCovPct1948))/sd(cc$tCovPct1948)

	#centered variables
	cc$cELEV<-(cc$ELEV-mean(cc$ELEV))
	cc$cSLOPE<-(cc$SLOPE-mean(cc$SLOPE))
	cc$cCURV<-(cc$CURV-mean(cc$CURV))
	cc$cCURV_PROF<-(cc$CURV_PROF-mean(cc$CURV_PROF))
	cc$cCURV_PLAN<-(cc$CURV_PLAN-mean(cc$CURV_PLAN))
	cc$cNORTHN<-(cc$NORTHN-mean(cc$NORTHN))
	cc$cEASTN<-(cc$EASTN-mean(cc$EASTN))
	cc$cTMI<-(cc$TMI-mean(cc$TMI))
	cc$ctCovPct1948<-(cc$tCovPct1948-mean(cc$tCovPct1948))

	cc$cINSOL<-(cc$INSOL-mean(cc$INSOL))
	cc$cDISTRIDGE<-(cc$DISTRIDGE-mean(cc$DISTRIDGE))
	cc$cHEATIND<-(cc$HEATIND-mean(cc$HEATIND))
	if (site!="WC")
		cc$cNEAR_DIST<-(cc$NEAR_DIST-mean(cc$NEAR_DIST))

	### flip the variables so positive should mean more cover

	## more moisture means more cover (wetter, more DF encr)
	cc$sSLOPE<- -cc$sSLOPE #more slope = more runoff = less wet
	cc$sCURV <- -cc$sCURV #more curv means less moisture less cover

	cc$sCURV_PLAN<- -cc$sCURV_PLAN
	#planform affects convergence/divergence
	#planform positive  = upward convex = less wet

	#cc$sCURV_PROF
	#profile affects acceleration/deceleration
	#profile negative = upward convex = less wet
	#profile positive = upward concave = more wet

	#cc$TMI #TMI higher is wetter is more cover

	## more exposure means less cover (drier, oaks comp. adv.)
	cc$sNORTHN #more north facing means less exposure
	#cc$sEASTN #more east facing means less exposure
	cc$sINSOL<- -cc$sINSOL # more insol means more exposure
	cc$sHEATIND<- -cc$sHEATIND #more heatind means more exposure

	## context - closer to df should be more cover
	#cc$sELEV 
		# for WC, high elev is closer to df
	cc$sDISTRIDGE<- -cc$sDISTRIDGE
		# for WC, closer to ridge is closer to df, more cover
	if (site!="WC"){
		cc$sELEV<- -cc$sELEV 
			#for others, lower elevation closer to df
		cc$sNEAR_DIST<- -cc$sNEAR_DIST
			# further from prairie usually means more df
		#cc$sDISTRIDGE
			# for others, closer to ridge means farther from df
	}


	#larger stCovPct1948 already should mean more cover


	### PCAs of variables in groups
	runoff<-princomp(cc[,c	("sCURV","sCURV_PROF","sCURV_PLAN","sTMI","sSLOPE")])
	if(site !="WC"){
		localcontext<-princomp(cc[,c		("sELEV","sDISTRIDGE","sNEAR_DIST")])
	} else {
		localcontext<-princomp(cc[,c							("sELEV","sDISTRIDGE")])
	}
	exposure<-princomp(cc[,c	("sNORTHN","sEASTN","sINSOL","sHEATIND")])

	cc$runoff1<-runoff$scores[,1]
	cc$localcontext1<-localcontext$scores[,1]
	cc$exposure1<-exposure$scores[,1]
	cc$runoff2<-runoff$scores[,2]
	cc$localcontext2<-localcontext$scores[,2]
	cc$exposure2<-exposure$scores[,2]

	#pulling the variance accounted for from the first component
	PCA.variance[[as.character(10*i)]]<-c(
		runoff=sub("Cumulative Proportion\\s+(\\d\\.\\d+)\\s+(\\d\\.\\d+).+","\\1",capture.output(summary(runoff))[5],perl=TRUE),
		localcontext=sub("Cumulative Proportion\\s+(\\d\\.\\d+)\\s+(\\d\\.\\d+).+","\\1",capture.output(summary(localcontext))[5],perl=TRUE),
		exposure=sub("Cumulative Proportion\\s+(\\d\\.\\d+)\\s+(\\d\\.\\d+).+","\\1",capture.output(summary(exposure))[5],perl=TRUE) )

	PCA.cor[[as.character(10*i)]]<-cor(cc[,c("runoff1","runoff2","localcontext1","localcontext2","exposure1","exposure2","stCovPct1948")])

	################################################################
	#-----------------plot data-----------------------------
	################################################################

	pdf(paste("AllData_",site,"_",i,".pdf",sep=""))

	hist(cc$COVER1948)
	hist(cc$COVER2009)

	hist(cc$ELEV) 
	hist(cc$SLOPE) 
	hist(cc$NORTHN)
	hist(cc$EASTN)
	hist(cc$CURV)
	hist(cc$TMI) 

	hist(cc$INSOL) 
	hist(cc$DISTRIDGE) 
	hist(cc$HEATIND) 
	if(site !="WC")
		hist(cc$NEAR_DIST) 

	hist(cc$runoff1)
	hist(cc$runoff2)
	hist(cc$localcontext1)
	hist(cc$localcontext2)
	hist(cc$exposure1)
	hist(cc$exposure2)

	par(mfrow=c(2,3))
	plot(cc$cov.pct.2009~cc$ELEV)
	plot(cc$cov.pct.2009~cc$SLOPE)
	plot(cc$cov.pct.2009~cc$CURV)
	plot(cc$cov.pct.2009~cc$NORTHN)
	plot(cc$cov.pct.2009~cc$EASTN)
	plot(cc$cov.pct.2009~cc$TMI)

	plot(cc$cov.pct.2009~cc$INSOL)
	plot(cc$cov.pct.2009~cc$DISTRIDGE)
	plot(cc$cov.pct.2009~cc$HEATIND)
	if(site != "WC")
		plot(cc$cov.pct.2009~cc$NEAR_DIST)
	par(mfrow=c(1,1))

	plot(cc$cov.pct.2009~cc$runoff1)
	plot(cc$cov.pct.2009~cc$runoff2)
	plot(cc$cov.pct.2009~cc$localcontext1)
	plot(cc$cov.pct.2009~cc$localcontext2)
	plot(cc$cov.pct.2009~cc$exposure1)
	plot(cc$cov.pct.2009~cc$exposure2)

	plot(cc$cov.pct.2009~cc$cov.pct.1948)

	################################################################
	#-----------------create neighborhood objects-------------
	################################################################

	coords<-as.matrix(cbind(cc$cXCoord,cc$cYCoord))
	nb<-dnearneigh(coords,0,nb.dist) 
	nb.w<-nb2listw(nb, glist=NULL, style="W", zero.policy=TRUE)
	mrf.fac <- as.factor(1:length(nb)) ## this is the nb your code already sets up
	names(nb) <- mrf.fac

	################################################################
	#-----------------fit models-----------------------------------
	################################################################
	gamknots<-2*round(nrow(cc)/10,0)
#	gamknots<-round(nrow(cc)/10,0)
	print(gamknots)

	model.time<-system.time(tempgamfit <- gam(cbind(round(cov.pct.2009 * 100), 100-round(cov.pct.2009 * 100)) ~ 
		+runoff1
		+exposure1
		+localcontext1
		+stCovPct1948
		+s(mrf.fac, bs="mrf", xt = list(nb = nb), k = gamknots ),
		data=cc, family = quasibinomial) )

	GlobMT1.1<- moran.test(residuals(tempgamfit), listw=nb.w)
	print(GlobMT1.1)
	mtgam<-GlobMT1.1$p.value
	clg <- correlog(cc$cXCoord, cc$cYCoord, residuals(tempgamfit),na.rm=T, increment=1, resamp=0)
	tempsummary<-summary(tempgamfit)

	gamfit[[as.character(10*i)]]<-tempgamfit
	gamfit.summary[[as.character(10*i)]]<-tempsummary
	mt.GAM[[as.character(10*i)]]<-mtgam
	timings[[as.character(10*i)]]<-model.time[["elapsed"]]
	num.knots[[as.character(10*i)]]<-gamknots
	scaleparm[[as.character(10*i)]]<-tempsummary$scale	
	correl.GAM[[as.character(10*i)]]<-clg
	sig.spat[[as.character(10*i)]]<-tempsummary$s.table[,"p-value"]
	resid.norm[[as.character(10*i)]]<-shapiro.test(residuals(tempgamfit))$p.value


	dev.off()

} # end loop over scales

	################################################################
	#-----------------extract parameter estimates-------------
	################################################################


get.parameter.estimates2 <-function(gamlist.summ, varname, scalenames) {
	parm.ests<-data.frame(est=numeric(),sd=numeric(),sig=numeric(),scale=numeric(),stringsAsFactors=FALSE )
	counter<-1
	for (i in scalenames){
		parm.ests[counter,]<- c(
			gamlist.summ[[ i ]]$p.table[varname,"Estimate"],
			gamlist.summ[[ i ]]$p.table[varname,"Std. Error"],
			gamlist.summ[[ i ]]$p.table[varname,"Pr(>|t|)"],
			as.numeric(as.character(i)) )
		counter<-counter+1
	}
	parm.ests$LI<-parm.ests$est-2*parm.ests$sd
	parm.ests$UI<-parm.ests$est+2*parm.ests$sd	
	return(parm.ests)
}


	runoff1<-get.parameter.estimates2(gamfit.summary,"runoff1",as.character(10*2:10))
	localcontext1<-get.parameter.estimates2(gamfit.summary,"localcontext1",as.character(10*2:10))
	PCOV<-get.parameter.estimates2(gamfit.summary,"stCovPct1948",as.character(10*2:10))
	exposure1<-get.parameter.estimates2(gamfit.summary,"exposure1",as.character(10*2:10))

save.image(paste(path,site,"_ChangeModeling_quasibinom_PCAvar1stcomp_GAM_2xknots.RData",sep=""))
