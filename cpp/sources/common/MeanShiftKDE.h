#ifndef MEANSHIFTKDE
#define MEANSHIFTKDE
#include "Estimate.h"

#include <Eigen/Dense>
using Eigen::MatrixXd;
using Eigen::VectorXd;

void MeanShiftKDE(const InputParam &input, const MatrixXd &remainCarrier, const MatrixXd &remainJacobian,
	const double &scale, VectorXd &theta, double &mode);

#endif
