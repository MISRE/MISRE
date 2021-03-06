/*	Functions.h
This file contains all functions requireded 
for the estimation of specific model.

For different objective functions, this file
(and the cpp file for implementation) should 
be modified accordingly.
*/

#ifndef FUNCTIONS
#define FUNCTIONS

#include "Estimate.h"
#include <Eigen/Dense>
using Eigen::MatrixXd;
using Eigen::VectorXd;

void CarrierGen(const InputParam &, const V_SIZE_T &, MatrixXd &);
void JacobianGen(const InputParam &, const V_SIZE_T &, MatrixXd &);
bool DLTsolve(const InputParam &, const V_SIZE_T &, VectorXd &);

#endif
